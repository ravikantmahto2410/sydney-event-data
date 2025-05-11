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
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Uncomment for production
        service = Service('D:/Ravikant/Btech/Coding 2/Louder Project/01_SYDNEY/chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def parse(self, response):
        page = response.meta.get('page', 1)
        max_pages = 5

        self.logger.info(f"Parsing page {page}: {response.url}")
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
        self.logger.info(f"Found {len(events)} event cards on this page")
        if not events:
            self.logger.info("No events found on this page.")
            self.driver.quit()
            return

        for event in events:
            item = EventItem()
            try:
                title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
                item['title'] = title_tag.get_text(strip=True) if title_tag else ''
                self.logger.info(f"Extracted title: {item['title']}")
            except Exception as e:
                self.logger.warning(f"Title not found: {e}")
                item['title'] = ''

            try:
                p_elements = event.select('p.Typography_root__487rx')

                item['date'] = p_elements[0].get_text(strip=True) if len(p_elements) > 0 else ''
                self.logger.info(f"Extracted date: {item['date']}")

                item['venue'] = p_elements[1].get_text(strip=True) if len(p_elements) > 1 else ''
                self.logger.info(f"Extracted venue: {item['venue']}")

                item['description'] = p_elements[3].get_text(strip=True) if len(p_elements) > 3 else ''
                self.logger.info(f"Extracted description (organizer): {item['description']}")
            except Exception as e:
                self.logger.warning(f"Date, Venue, or Description not found: {e}")
                item['date'] = ''
                item['venue'] = ''
                item['description'] = ''

            try:
                item['ticket_url'] = event.select_one('a:has(h3)')['href'] if event.select_one('a:has(h3)') else ''
                self.logger.info(f"Extracted ticket_url: {item['ticket_url']}")
            except Exception as e:
                self.logger.warning(f"Ticket URL not found: {e}")
                item['ticket_url'] = ''

            self.logger.info(f"Scraped item: {item}")
            yield item

        if page >= max_pages:
            self.logger.info(f"Reached maximum page limit of {max_pages}. Stopping pagination.")
            self.driver.quit()
            return

        self.logger.info("Looking for 'Explore More Events' link...")
        try:
            explore_more_link = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Explore More Events")]'))
            )
            next_url = explore_more_link.get_attribute('href')
            if next_url and next_url != response.url:
                self.logger.info(f"Following next page: {next_url}")
                yield scrapy.Request(next_url, callback=self.parse, meta={'page': page + 1})
            else:
                self.logger.info("No valid next page found. Stopping pagination.")
                self.driver.quit()
        except TimeoutException:
            self.logger.info("No 'Explore More Events' link found. Stopping pagination.")
            self.driver.quit()