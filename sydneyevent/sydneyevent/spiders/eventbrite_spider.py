import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
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
            # Extract title
            try:
                title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
                item['title'] = title_tag.get_text(strip=True) if title_tag else ''
                self.logger.info(f"Extracted title: {item['title']}")
            except Exception as e:
                self.logger.warning(f"Title not found: {e}")
                item['title'] = ''

            # Initialize item fields
            item['date'] = ''
            item['venue'] = ''
            item['description'] = ''
            try:
                p_elements = event.select('p.Typography_root__487rx')
                self.logger.debug(f"Found {len(p_elements)} <p> tags: {[p.get_text(strip=True) for p in p_elements]}")

                promotional_tags = {'selling quickly', 'nearly full', 'sales end soon', 'promoted', 'free', 'just added'}

                # Process all <p> tags without breaking
                for p in p_elements:
                    text = p.get_text(strip=True).lower()
                    # Look for date patterns
                    if not item['date'] and any(keyword in text for keyword in ['am', 'pm', 'today', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                        raw_date = p.get_text(strip=True)
                        self.logger.info(f"Scraped raw date for {item['title']}: {raw_date}")
                        item['date'] = raw_date
                    # Look for description
                    elif 'ticket price' in text:
                        item['description'] = p.get_text(strip=True)
                    # Look for venue, only set if not already set
                    elif text not in promotional_tags and not item['venue']:
                        item['venue'] = p.get_text(strip=True)

                # If no date was found in <p> tags, try extracting from the title
                if not item['date']:
                    title_lower = item['title'].lower()
                    # Look for patterns like "fri 16 may", "sun 18th may", etc.
                    date_pattern = r'(mon|tue|wed|thu|fri|sat|sun)\s+\d{1,2}(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
                    match = re.search(date_pattern, title_lower)
                    if match:
                        item['date'] = match.group(0).title()  # Capitalize the extracted date (e.g., "Sun 18th May")
                        self.logger.info(f"Extracted date from title for {item['title']}: {item['date']}")

                self.logger.info(f"Extracted date: {item['date']}")
                self.logger.info(f"Extracted venue: {item['venue']}")
                self.logger.info(f"Extracted description: {item['description']}")
            except Exception as e:
                self.logger.warning(f"Failed to extract Date, Venue, or Description: {str(e)}")

            # Extract ticket URL
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