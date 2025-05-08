import os
import openai
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Load data
df = pd.read_csv("daily_prophet_summaries_40.csv")
titles = df["Title"].dropna().tolist()
summaries = df["Summary"].dropna().tolist()

# ✅ Helper: Extract top 5 themes using GPT
def extract_themes_from_list(text_list, label):
    joined = "\n".join(f"{i+1}. {t}" for i, t in enumerate(text_list))
    prompt = f"""These are {len(text_list)} {label} from a fan editorial site.

Identify the top 5 most common themes, each phrased in 4–7 words. 
Return them as a numbered list from most to least common.

Items:
{joined}
"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
    )
    lines = response.choices[0].message.content.strip().split("\n")
    return [line.split(".", 1)[1].strip() for line in lines if "." in line]

# ✅ Step 1: Get themes
themes_from_titles = extract_themes_from_list(titles, "titles")
themes_from_summaries = extract_themes_from_list(summaries, "one-sentence summaries")

# ✅ Step 2: Generate embeddings using Ada-002
def get_embedding(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return np.array(response.data[0].embedding)

title_embeddings = [get_embedding(theme) for theme in themes_from_titles]
summary_embeddings = [get_embedding(theme) for theme in themes_from_summaries]

# ✅ Step 3: Compute cosine similarity
similarity_matrix = cosine_similarity(title_embeddings, summary_embeddings)
best_match_scores = similarity_matrix.max(axis=1)
best_matches = similarity_matrix.argmax(axis=1)
difference_scores = 1 - best_match_scores
average_diff = round(difference_scores.mean(), 3)

# ✅ Step 4: Display output
print("\n🎯 Top 5 Themes from Titles:")
for i, theme in enumerate(themes_from_titles, 1):
    print(f"{i}. {theme}")

print("\n🧠 Top 5 Themes from Summaries:")
for i, theme in enumerate(themes_from_summaries, 1):
    print(f"{i}. {theme}")

print(f"\n📉 Average Semantic Difference Score: {average_diff:.3f}")

# ✅ Step 5: Save comparison to CSV
result_df = pd.DataFrame({
    "Title Theme": themes_from_titles,
    "Closest Summary Theme": [themes_from_summaries[i] for i in best_matches],
    "Similarity Score": best_match_scores,
    "Difference Score": difference_scores
})

result_df.to_csv("theme_overlap_analysis.csv", index=False)
print("\n✅ Saved to 'theme_overlap_analysis.csv'")
