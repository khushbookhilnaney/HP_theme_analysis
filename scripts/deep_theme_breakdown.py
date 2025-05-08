import os
import openai
import pandas as pd
from dotenv import load_dotenv

# ✅ Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Load the CSV file with summaries
df = pd.read_csv("daily_prophet_summaries_40.csv")
summaries = df["Summary"].dropna().tolist()

# ✅ Combine summaries into numbered list
combined_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(summaries))

# ✅ Prompt GPT for top 5 themes
theme_prompt = f"""These are 40 one-sentence summaries of editorial articles from a fan website.

Each sentence captures the core idea of one article. Based on these summaries, identify and list the *top 5 most common themes*, each phrased in 4–7 words.

Order them from most to least common and don't repeat. Only give a numbered list with short theme names.

Summaries:
{combined_text}
"""

# ✅ Call OpenAI to extract top themes
theme_response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": theme_prompt}],
    max_tokens=300,
    temperature=0.3,
)

# ✅ Parse theme list
themes_text = theme_response.choices[0].message.content.strip()
theme_lines = [line.strip() for line in themes_text.split("\n") if line.strip()]
theme_data = []
for line in theme_lines:
    if "." in line:
        num, theme = line.split(".", 1)
        theme_data.append({"Rank": int(num.strip()), "Theme": theme.strip()})

themes_df = pd.DataFrame(theme_data)
themes_df.to_csv("top_5_editorial_themes.csv", index=False, encoding="utf-8")
print("✅ Top 5 themes saved to 'top_5_editorial_themes.csv'")

# ✅ Deep dive into each theme
detailed_breakdowns = []
for theme in themes_df["Theme"]:
    sub_prompt = f"""
These are 40 one-sentence summaries of editorial articles from a Harry Potter fan website.

The identified recurring theme is: **{theme}**

Based on these summaries, provide a **5–7 line deep dive** into how this theme appears. Include:
- Specific characters involved
- Subtopics or lenses (e.g., identity, psychology)
- Concrete instances or angles (e.g., Luna Lovegood and neurodivergence)

Use numbered points if possible. Be specific, not generic.

Summaries:
{combined_text}
"""
    try:
        sub_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": sub_prompt}],
            max_tokens=500,
            temperature=0.5,
        )
        breakdown = sub_response.choices[0].message.content.strip()
        detailed_breakdowns.append({"Theme": theme, "Breakdown": breakdown})
        print(f"✅ Expanded: {theme}")
    except Exception as e:
        print(f"❌ Failed to expand {theme}: {e}")

# ✅ Save detailed breakdowns
breakdown_df = pd.DataFrame(detailed_breakdowns)
breakdown_df.to_csv("theme_breakdowns.csv", index=False, encoding="utf-8")
print("✅ Saved detailed theme breakdowns to 'theme_breakdowns.csv'")
