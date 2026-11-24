import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

API = "http://127.0.0.1:8765/analyze"
OUT = Path("frontend/demo-data.js")

# The example texts. The web page reads them from the saved file, so the page and the results always match.
EXAMPLES = {
    "news": "The city council voted on Tuesday to approve a new transport budget after months of debate. Council members backed the plan by nine votes to four. A spokesperson said road repairs will begin next month in phases to limit disruption, and residents will receive notices at least two weeks before work starts in their area.",
    "clickbait": "SHOCKING secret about your electricity bill that the power companies DON'T want you to know! You will NOT believe what happens when you do this one simple thing at home tonight. Experts are STUNNED, and the so-called authorities are staying silent. Share this with everyone you love before it gets deleted! Wake up, people! They have been lying to you for years.",
    "claim": "5G towers cause symptoms",
    "calm": "A local community group said on Tuesday that 5G towers cause health symptoms such as headaches and sleeplessness, and asked the council to pause new installations. A council spokesperson said the request would be discussed at next month's meeting, and that the towers meet national safety guidelines. Residents are invited to submit written comments by the end of the month.",
}


def analyze(text):
    """Send one text to the running local API and return its JSON answer."""
    request = urllib.request.Request(
        API,
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


demo = {}
for key, text in EXAMPLES.items():
    print("analyzing:", key)
    try:
        result = analyze(text)
    except (urllib.error.URLError, TimeoutError) as error:
        sys.exit(f"Could not reach the API at {API} ({type(error).__name__}). "
                 "Start it first: uvicorn api:app --app-dir src --port 8765")
    demo[key] = {"text": text, "recorded_at": date.today().strftime("%d %b %Y"), "result": result}
    time.sleep(1)   # stay well below the server's limit of 10 requests per minute

OUT.write_text("window.DEMO_RESULTS = " + json.dumps(demo, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
print("saved:", OUT)
for key, item in demo.items():
    res = item["result"]
    print(f"  {key:10s} style = {res['style']['verdict']:16s} fact-checks = {res['fact_checks']['status']}"
          f" (close {len(res['fact_checks']['close_matches'])}, related {len(res['fact_checks']['related'])})")
