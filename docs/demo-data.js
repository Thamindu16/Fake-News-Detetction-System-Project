window.DEMO_RESULTS = {
  "news": {
    "text": "The city council voted on Tuesday to approve a new transport budget after months of debate. Council members backed the plan by nine votes to four. A spokesperson said road repairs will begin next month in phases to limit disruption, and residents will receive notices at least two weeks before work starts in their area.",
    "recorded_at": "22 Nov 2026",
    "result": {
      "style": {
        "verdict": "news_site_style",
        "message": "The writing style closely resembles articles from ordinary news websites in the training data.",
        "words": 55,
        "reliability": "limited",
        "only_start_read": false
      },
      "fact_checks": {
        "status": "none_found",
        "close_matches": [],
        "related": []
      },
      "warnings": [
        {
          "code": "style_only",
          "message": "The style result describes how the text is written. It says nothing about whether the content is true."
        },
        {
          "code": "short_text",
          "message": "The text has fewer than 80 words, so the style result is less reliable."
        },
        {
          "code": "no_fact_checks",
          "message": "No related fact-checks were found. This does not mean the content is true; it may simply not have been checked."
        }
      ]
    }
  },
  "clickbait": {
    "text": "SHOCKING secret about your electricity bill that the power companies DON'T want you to know! You will NOT believe what happens when you do this one simple thing at home tonight. Experts are STUNNED, and the so-called authorities are staying silent. Share this with everyone you love before it gets deleted! Wake up, people! They have been lying to you for years.",
    "recorded_at": "22 Nov 2026",
    "result": {
      "style": {
        "verdict": "fake_site_style",
        "message": "The writing style closely resembles articles from fake-news websites in the training data.",
        "words": 62,
        "reliability": "limited",
        "only_start_read": false
      },
      "fact_checks": {
        "status": "none_found",
        "close_matches": [],
        "related": []
      },
      "warnings": [
        {
          "code": "style_only",
          "message": "The style result describes how the text is written. It says nothing about whether the content is true."
        },
        {
          "code": "short_text",
          "message": "The text has fewer than 80 words, so the style result is less reliable."
        },
        {
          "code": "no_fact_checks",
          "message": "No related fact-checks were found. This does not mean the content is true; it may simply not have been checked."
        }
      ]
    }
  },
  "claim": {
    "text": "5G towers cause symptoms",
    "recorded_at": "22 Nov 2026",
    "result": {
      "style": {
        "verdict": "too_short",
        "message": "This text is too short for a style analysis (at least 40 words are needed).",
        "words": 4,
        "reliability": null,
        "only_start_read": false
      },
      "fact_checks": {
        "status": "ok",
        "close_matches": [],
        "related": [
          {
            "matched_claim": "The signals emitted by 5G towers are damaging to humans, animals and plants, and can cause health conditions, including heart and vision problems.",
            "rating": "There is no evidence that 5G technology is harmful to human health when used within the recommended exposure limits.",
            "publisher": "Full Fact",
            "url": "https://fullfact.org/health/5g-poster-harmful-health-inaccurate/",
            "review_date": "2026-01-13T00:00:00Z",
            "your_text_part": "5G towers cause symptoms"
          },
          {
            "matched_claim": "The signals emitted by 5G towers are damaging to humans, animals and plants.",
            "rating": "There is no evidence that 5G or similar radiofrequency technology is harmful when used within the recommended exposure limits.",
            "publisher": "Full Fact",
            "url": "https://fullfact.org/health/5G-towers-humans-animals-plants/",
            "review_date": "2025-01-09T00:00:00Z",
            "your_text_part": "5G towers cause symptoms"
          },
          {
            "matched_claim": "5G towers are used for weather engineering",
            "rating": "False",
            "publisher": "AFP Fact Check",
            "url": "https://factcheck.afp.com/doc.afp.com.B3DA4CQ",
            "review_date": "2026-05-20T20:56:00Z",
            "your_text_part": "5G towers cause symptoms"
          }
        ]
      },
      "warnings": [
        {
          "code": "style_only",
          "message": "The style result describes how the text is written. It says nothing about whether the content is true."
        },
        {
          "code": "too_short",
          "message": "This text is too short for a style analysis (at least 40 words are needed)."
        },
        {
          "code": "match_meaning",
          "message": "Each rating applies to the matched claim shown next to it, not to your text. A matched claim can even say the opposite of your text."
        }
      ]
    }
  },
  "calm": {
    "text": "A local community group said on Tuesday that 5G towers cause health symptoms such as headaches and sleeplessness, and asked the council to pause new installations. A council spokesperson said the request would be discussed at next month's meeting, and that the towers meet national safety guidelines. Residents are invited to submit written comments by the end of the month.",
    "recorded_at": "22 Nov 2026",
    "result": {
      "style": {
        "verdict": "news_site_style",
        "message": "The writing style closely resembles articles from ordinary news websites in the training data.",
        "words": 60,
        "reliability": "limited",
        "only_start_read": false
      },
      "fact_checks": {
        "status": "none_found",
        "close_matches": [],
        "related": []
      },
      "warnings": [
        {
          "code": "style_only",
          "message": "The style result describes how the text is written. It says nothing about whether the content is true."
        },
        {
          "code": "short_text",
          "message": "The text has fewer than 80 words, so the style result is less reliable."
        },
        {
          "code": "no_fact_checks",
          "message": "No related fact-checks were found. This does not mean the content is true; it may simply not have been checked."
        }
      ]
    }
  }
};
