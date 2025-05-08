import subprocess

steps = [
    ("Scraping articles", "scripts/scrape_articles.py"),
    ("Summarizing articles", "scripts/summarize_articles.py"),
    ("Extracting themes from titles and summaries", "scripts/extract_themes.py"),
    ("Analyzing theme similarity", "scripts/analyze_similarity.py"),
    ("Generating detailed theme breakdowns", "scripts/deep_theme_breakdown.py")
]

for description, script_path in steps:
    print(f"\n🚀 Running step: {description} ({script_path})")
    result = subprocess.run(['python', script_path], capture_output=True)

    if result.returncode != 0:
        print(f"❌ Error while running {script_path}:")
        print(result.stderr.decode())
        break
    else:
        print(f"✅ Completed: {description}\n{result.stdout.decode()}")