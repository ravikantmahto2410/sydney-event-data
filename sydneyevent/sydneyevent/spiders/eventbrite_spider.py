from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Selenium WebDriver
chrome_options = Options()
# Comment out headless mode for debugging
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

# Find event cards
events = driver.find_elements(By.CSS_SELECTOR, 'div.small-card-mobile.eds-l-pad-all-2')
print(f"Found {len(events)} event cards")

# Extract fields from each event card
for event in events:
    print("\n--- Event Card ---")
    # Title
    try:
        # Wait for the <h3> tag to ensure it's rendered
        WebDriverWait(event, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h3'))
        )
        # Try multiple selectors for robustness
        try:
            title = event.find_element(By.CSS_SELECTOR, 'h3.event-card__title-text').text.strip()
            print(f"Title: {title}")
        except:
            try:
                title = event.find_element(By.CSS_SELECTOR, 'h3.eds-text-h3').text.strip()
                print(f"Title (fallback 1): {title}")
            except:
                title = event.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                print(f"Title (fallback 2): {title}")
    except:
        print("Title not found")

    # Get all <p> tags to differentiate date, venue, and description
    try:
        # Use a more generic selector for <p> tags
        p_elements = event.find_elements(By.CSS_SELECTOR, 'p[class*="eds-text-body"]')

        # Date (first <p>)
        date = p_elements[0].text.strip() if len(p_elements) > 0 else ''
        print(f"Date: {date}")

        # Venue (second <p>)
        venue = p_elements[1].text.strip() if len(p_elements) > 1 else ''
        print(f"Venue: {venue}")

        # Description/Organizer (fourth <p>)
        description = p_elements[3].text.strip() if len(p_elements) > 3 else ''
        print(f"Description (organizer): {description}")
    except:
        print("Date, Venue, or Description not found")

    # Ticket URL
    try:
        ticket_url = event.find_element(By.CSS_SELECTOR, 'a:has(h3)').get_attribute('href')
        print(f"Ticket URL: {ticket_url}")
    except:
        print("Ticket URL not found")

driver.quit()