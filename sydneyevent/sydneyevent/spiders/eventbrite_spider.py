import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
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
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def parse(self, response):
        # Use Selenium to load the page
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

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        events = soup.select('div.small-card-mobile.eds-l-pad-all-2')
        self.logger.info(f"Found {len(events)} event cards")  # pylint: disable=undefined-variable

        # Deduplicate events based on title and ticket URL
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

        self.logger.info(f"After deduplication, found {len(unique_events)} unique event cards")  # pylint: disable=undefined-variable

        # Extract fields from each event card
        for event in unique_events:
            item = EventItem()
            try:
                title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
                item['title'] = title_tag.get_text(strip=True) if title_tag else ''
                self.logger.info(f"Extracted title: {item['title']}")  # pylint: disable=undefined-variable
            except Exception as e:
                self.logger.warning(f"Title not found: {e}")  # pylint: disable=undefined-variable
                item['title'] = ''

            item['date'] = ''
            item['venue'] = ''
            item['description'] = ''
            try:
                p_elements = event.select('p.Typography_root__487rx')
                self.logger.debug(f"Found {len(p_elements)} <p> tags: {[p.get_text(strip=True) for p in p_elements]}")  # pylint: disable=undefined-variable

                # Promotional tags to exclude from venue
                promotional_tags = {'selling quickly', 'nearly full', 'sales end soon', 'promoted', 'free', 'just added'}

                # Assign fields based on content
                for p in p_elements:
                    text = p.get_text(strip=True).lower()
                    # Check if the text looks like a date
                    if any(keyword in text for keyword in ['am', 'pm', 'today', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) and any(char.isdigit() for char in text):
                        item['date'] = p.get_text(strip=True)
                    # Check if the text looks like a description
                    elif 'ticket price' in text:
                        item['description'] = p.get_text(strip=True)
                    # Check if the text looks like a venue
                    elif text not in promotional_tags:
                        item['venue'] = p.get_text(strip=True)

                self.logger.info(f"Extracted date: {item['date']}")  # pylint: disable=undefined-variable
                self.logger.info(f"Extracted venue: {item['venue']}")  # pylint: disable=undefined-variable
                self.logger.info(f"Extracted description (organizer): {item['description']}")  # pylint: disable=undefined-variable
            except Exception as e:
                self.logger.warning(f"Failed to extract Date, Venue, or Description: {str(e)}")  # pylint: disable=undefined-variable

            try:
                item['ticket_url'] = event.select_one('a:has(h3)')['href'] if event.select_one('a:has(h3)') else ''
                self.logger.info(f"Extracted ticket_url: {item['ticket_url']}")  # pylint: disable=undefined-variable
            except Exception as e:
                self.logger.warning(f"Ticket URL not found: {e}")  # pylint: disable=undefined-variable
                item['ticket_url'] = ''

            self.logger.info(f"Scraped item: {item}")  # pylint: disable=undefined-variable
            yield item

    def closed(self, reason):
        self.driver.quit()
        self.logger.info("WebDriver closed")  # pylint: disable=undefined-variable