import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ..items import EventItem

class EventbriteSpider(scrapy.Spider):
    name = 'eventbrite'
    allowed_domains = ['eventbrite.com.au']
    start_urls = ['https://www.eventbrite.com.au/d/australia--sydney/events/']

    def __init__(self, *args, **kwargs):
        super(EventbriteSpider, self).__init__(*args, **kwargs)
        try:
            chrome_options = Options()
            # chrome_options.add_argument('--headless')  # Uncomment for production
            service = Service('D:/Ravikant/Btech/Coding 2/Louder Project/01_SYDNEY/chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def parse(self, response):
        self.driver.get(response.url)
        try:
            self.logger.info("Waiting for event cards to load...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.small-card-mobile.eds-l-pad-all-2'))
            )
        except TimeoutException:
            self.logger.error("Failed to load events: Timeout waiting for event cards")
            self.driver.quit()
            return

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        events = soup.select('div.small-card-mobile.eds-l-pad-all-2')
        self.logger.info(f"Found {len(events)} event cards")

        seen_keys = set()
        unique_events = []
        for event in events:
            title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
            title = title_tag.get_text(strip=True) if title_tag else ''
            ticket_url = event.select_one('a:has(h3)')['href'] if event.select_one('a:has(h3)') else ''
            key = (title, ticket_url)
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_events.append(event)

        self.logger.info(f"After deduplication, found {len(unique_events)} unique event cards")

        for event in unique_events:
            item = EventItem()
            try:
                title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
                item['title'] = title_tag.get_text(strip=True) if title_tag else ''
                self.logger.info(f"Extracted title: {item['title']}")
            except Exception as e:
                self.logger.warning(f"Title not found: {e}")
                item['title'] = ''

            item['date'] = ''
            item['venue'] = ''
            item['description'] = ''
            try:
                p_elements = event.select('p.Typography_root__487rx')
                self.logger.debug(f"Found {len(p_elements)} <p> tags: {[p.get_text(strip=True) for p in p_elements]}")

                promotional_tags = {'selling quickly', 'nearly full', 'sales end soon', 'promoted', 'free', 'just added'}

                current_date = datetime.now()
                for p in p_elements:
                    text = p.get_text(strip=True).lower()
                    if any(keyword in text for keyword in ['am', 'pm', 'today', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) and any(char.isdigit() for char in text):
                        raw_date = p.get_text(strip=True)
                        try:
                            if "today" in text:
                                time_part = raw_date.replace("Today at ", "").strip()
                                parsed_time = datetime.strptime(time_part, "%I:%M %p")
                                item['date'] = current_date.replace(
                                    hour=parsed_time.hour,
                                    minute=parsed_time.minute,
                                    second=0,
                                    microsecond=0
                                ).strftime("%Y-%m-%d %H:%M:%S")
                            elif "yesterday" in text:
                                time_part = raw_date.replace("Yesterday at ", "").strip()
                                parsed_time = datetime.strptime(time_part, "%I:%M %p")
                                yesterday = current_date - timedelta(days=1)
                                item['date'] = yesterday.replace(
                                    hour=parsed_time.hour,
                                    minute=parsed_time.minute,
                                    second=0,
                                    microsecond=0
                                ).strftime("%Y-%m-%d %H:%M:%S")
                            else:
                                # Try parsing as an absolute date (e.g., "Mon, May 15, 2025 at 6:00 PM")
                                try:
                                    parsed_date = datetime.strptime(raw_date, "%a, %b %d, %Y at %I:%M %p")
                                    item['date'] = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    # Try another common format (e.g., "2025-05-15 18:00:00")
                                    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
                                    item['date'] = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError as e:
                            self.logger.warning(f"Failed to parse date '{raw_date}': {e}")
                            item['date'] = current_date.strftime("%Y-%m-%d %H:%M:%S")  # Fallback to current date
                    elif 'ticket price' in text:
                        item['description'] = p.get_text(strip=True)
                    elif text not in promotional_tags:
                        item['venue'] = p.get_text(strip=True)

                self.logger.info(f"Extracted date: {item['date']}")
                self.logger.info(f"Extracted venue: {item['venue']}")
                self.logger.info(f"Extracted description: {item['description']}")
            except Exception as e:
                self.logger.warning(f"Failed to extract Date, Venue, or Description: {str(e)}")

            try:
                item['ticket_url'] = event.select_one('a:has(h3)')['href'] if event.select_one('a:has(h3)') else ''
                self.logger.info(f"Extracted ticket_url: {item['ticket_url']}")
            except Exception as e:
                self.logger.warning(f"Ticket URL not found: {e}")
                item['ticket_url'] = ''

            self.logger.info(f"Scraped item: {item}")
            yield item

    def closed(self, reason):
        self.driver.quit()
        self.logger.info("WebDriver closed")