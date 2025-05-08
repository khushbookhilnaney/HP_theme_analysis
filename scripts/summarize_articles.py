import os
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Load environment variables from .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Setup Chrome in headless mode
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ URL format for editorial pages
base_url = "https://www.mugglenet.com/category/the-daily-prophet/editorials/page/{}/"

# ✅ Step 1: Scrape up to 40 latest articles
articles = []
page = 1
while len(articles) < 40:
    driver.get(base_url.format(page))
    time.sleep(2.5)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article")))
        article_elements = driver.find_elements(By.CSS_SELECTOR, "article")

        for art in article_elements:
            try:
                title_elem = art.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_elem.text.strip()
                link = title_elem.get_attribute("href").strip()
                if not any(a['Link'] == link for a in articles):
                    articles.append({"Title": title, "Link": link})
                if len(articles) >= 40:
                    break
            except:
                continue
    except Exception as e:
        print(f"❌ Error on page {page}: {e}")
        break

    page += 1

# ✅ Step 2: Summarize article content
summarized = []
for i, article in enumerate(articles):
    try:
        driver.get(article["Link"])
        time.sleep(2)

        # Accept cookies if prompted
        try:
            accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Accept")]')
            accept_btn.click()
            time.sleep(1)
        except:
            pass

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        content = " ".join([p.text.strip() for p in paragraphs if len(p.text.strip().split()) > 5][:5])

        if not content:
            print(f"⚠️ No valid content in: {article['Title']}")
            continue

        # ✅ Summarize using OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Summarize the following editorial in one sentence:\n\n{content}"}
            ],
            max_tokens=60,
            temperature=0.5
        )

        summary = response.choices[0].message.content.strip()
        summarized.append({
            "Title": article["Title"],
            "Link": article["Link"],
            "Summary": summary
        })
        print(f"✅ [{i+1}/40] Summarized: {article['Title']}")

    except Exception as e:
        print(f"❌ Error in {article['Title']}: {e}")
        continue

driver.quit()

# ✅ Save to CSV
df = pd.DataFrame(summarized)
df.to_csv("daily_prophet_summaries_40.csv", index=False, encoding="utf-8")
print("\n🎉 Done! 40 summaries saved to 'daily_prophet_summaries_40.csv'")
