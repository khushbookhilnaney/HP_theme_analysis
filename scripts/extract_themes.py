import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# ✅ Load .env and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Load summaries from CSV
df = pd.read_csv("daily_prophet_summaries_40.csv")
summaries = df["Summary"].dropna().tolist()

# ✅ Format summaries for prompt
summary_prompt_block = "\n".join(f"{i+1}. {s}" for i, s in enumerate(summaries))

# ✅ Prompt for themes from summaries
theme_prompt = f"""These are summaries of editorial articles.
Identify and list the top 5 most common themes, each 4–7 words long.
Only return a numbered list.

Summaries:
{summary_prompt_block}
"""

# ✅ Prompt for characters from summaries
character_prompt = f"""These are summaries of editorial articles.
Identify and list the top 5 most discussed characters from the Harry Potter universe based on these summaries.
Only return a numbered list of character names.

Summaries:
{summary_prompt_block}
"""

# ✅ Request themes from OpenAI
theme_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": theme_prompt}],
    temperature=0.3,
    max_tokens=300
)

# ✅ Request characters from OpenAI
character_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": character_prompt}],
    temperature=0.3,
    max_tokens=300
)

# ✅ Parse themes
themes_text = theme_response.choices[0].message.content.strip()
theme_lines = [line.strip() for line in themes_text.split("\n") if "." in line]
top_themes = [line.split(".", 1)[1].strip() for line in theme_lines]

# ✅ Parse characters
characters_text = character_response.choices[0].message.content.strip()
character_lines = [line.strip() for line in characters_text.split("\n") if "." in line]
top_characters = [line.split(".", 1)[1].strip() for line in character_lines]

# ✅ Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

# ✅ Save to CSV
pd.DataFrame({"Rank": list(range(1, 6)), "Theme": top_themes}).to_csv("outputs/top_5_summary_themes.csv", index=False)
pd.DataFrame({"Rank": list(range(1, 6)), "Character": top_characters}).to_csv("outputs/top_5_characters.csv", index=False)

# ✅ Done
print("✅ Top 5 themes saved to outputs/top_5_summary_themes.csv")
print("✅ Top 5 characters saved to outputs/top_5_characters.csv")

