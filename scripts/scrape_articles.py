import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options
options = Options()
options.add_argument("--headless=new")  # Run Chrome in headless mode
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection by websites
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

base_url = "https://www.mugglenet.com/tag/the-daily-prophet/page/{}/"
page = 1
all_articles = []

# Make sure the 'data' folder exists before saving the CSV
os.makedirs("data", exist_ok=True)

# Loop until we get 40 articles
while len(all_articles) < 40:
    print(f"📝 Scraping page {page}...")  # Show which page is being scraped
    driver.get(base_url.format(page))
    time.sleep(2.5)  # Let the page load

    # Find all article elements
    articles = driver.find_elements(By.TAG_NAME, "article")

    # If no articles are found, break out of the loop
    if not articles:
        print("⚠️ No articles found. Stopping scraping.")
        break

    # Loop through articles and scrape the titles and links
    for article in articles:
        try:
            # Try to locate the title and link of the article
            title_elem = article.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_elem.text.strip()
            link = title_elem.get_attribute("href")

            if title and link:  # Ensure both title and link exist
                all_articles.append([title, link])
                print(f"✅ Article added: {title}")  # Log when a new article is added
            
            if len(all_articles) >= 40:  # Stop if we have 40 articles
                break
        except Exception as e:
            print(f"❌ Error extracting article: {e}")
            continue

    page += 1  # Move to the next page

# Quit the driver after scraping
driver.quit()

# Save the scraped articles to a CSV file
try:
    with open("data/daily_prophet_summaries_40.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Link"])  # Write header
        writer.writerows(all_articles)  # Write article data
    print(f"✅ Scraped and saved {len(all_articles)} articles.")
except FileNotFoundError as e:
    print(f"❌ Error saving file: {e}")
