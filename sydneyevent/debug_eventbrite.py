from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up Selenium WebDriver
chrome_options = Options()
# chrome_options.add_argument('--headless')
service = Service('D:/Ravikant/Btech/Coding 2/Louder Project/01_SYDNEY/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the Eventbrite page
url = 'https://www.eventbrite.com.au/d/australia--sydney/events/'
driver.get(url)

# Wait for event cards to load
try:
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.small-card-mobile.eds-l-pad-all-2'))
    )
    print("Event cards loaded successfully")
except:
    print("Failed to load event cards")
    driver.quit()
    exit()

# Get the page source and parse it with BeautifulSoup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

# Find event cards using BeautifulSoup
events = soup.select('div.small-card-mobile.eds-l-pad-all-2')
print(f"Found {len(events)} event cards")

# Deduplicate events based on title
seen_titles = set()
unique_events = []
for event in events:
    title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
    title = title_tag.get_text(strip=True) if title_tag else ''
    if title and title not in seen_titles:
        seen_titles.add(title)
        unique_events.append(event)

print(f"After deduplication, found {len(unique_events)} unique event cards")

# Extract fields from each event card
for event in unique_events:
    print("\n--- Event Card ---")
    # Title
    title = ''
    try:
        title_tag = event.select_one('h3.event-card__title-text') or event.select_one('h3.eds-text-h3') or event.select_one('h3')
        title = title_tag.get_text(strip=True) if title_tag else ''
        print(f"Title: {title}")
    except:
        print("Title not found")

    # Get all <p> tags to differentiate date, venue, and description
    date = ''
    venue = ''
    description = ''
    try:
        p_tags = event.select('p.Typography_root__487rx')
        print(f"Found {len(p_tags)} <p> tags: {[p.get_text(strip=True) for p in p_tags]}")

        # Promotional tags to exclude from venue
        promotional_tags = {'selling quickly', 'nearly full', 'sales end soon', 'promoted', 'free', 'just added'}

        # Assign fields based on content
        for p in p_tags:
            text = p.get_text(strip=True).lower()
            # Check if the text looks like a date
            if any(keyword in text for keyword in ['am', 'pm', 'today', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) and any(char.isdigit() for char in text):
                date = p.get_text(strip=True)
            # Check if the text looks like a description
            elif 'ticket price' in text:
                description = p.get_text(strip=True)
            # Check if the text looks like a venue (relaxed conditions)
            elif text not in promotional_tags:
                venue = p.get_text(strip=True)

        print(f"Date: {date}")
        print(f"Venue: {venue}")
        print(f"Description (organizer): {description}")
    except:
        print("Date, Venue, or Description not found")

    # Ticket URL
    ticket_url = ''
    try:
        ticket_url = event.select_one('a:has(h3)')['href'] if event.select_one('a:has(h3)') else ''
        print(f"Ticket URL: {ticket_url}")
    except:
        print("Ticket URL not found")

driver.quit()