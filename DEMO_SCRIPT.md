# ARGUS Demo Script — about 4 minutes (limit 5:00)

Say it in your own words, on camera or in your own voice. **Bold = what to click.** Speak slowly; pauses are fine.

**Before recording:** `cd ~/Argus && git pull origin main && python3 -m streamlit run app.py`. Click through all 6 tabs once. Cmd+Shift+5 to record.

---

## 0:00 – Intro (Dashboard)
"Hi, I'm Sanskriti. This is ARGUS, a research tool for Charles Schwab's equity analysts. After every earnings release, analysts have to check whether what management *says* matches what the filings *show*. Wording shifts every quarter, and accounting baselines quietly change. I tested it on NVIDIA's last six quarters. Every calculation runs in plain Python, so there's no AI math to trust."

## 0:30 – Dashboard (scroll down slowly)
"Here are the seven findings, sorted into the four categories.
In the latest quarter, revenue grew about 18%. But operating cash flow *fell* 52%, because receivables jumped 55% to $63 billion. That's the main thing worth asking management about.
Second, management guided operating expense growth to the 'high-30s.' Actual growth was 40.7% GAAP and 42.5% non-GAAP.
Third, NVIDIA changed how it treats stock comp and restated old numbers. Last year's Q4 non-GAAP expenses went from $5.1 billion to $6.7 billion. Anyone splicing old and new data would get a fake spike."

## 1:20 – Timeline
**Timeline** tab → dropdown → **GAAP Operating Cash Flow**.
"Every number has its units, period and a link to the filing." *(Open one filing expander to show the link.)*

## 1:40 – Evidence Explorer
**Evidence Explorer** → select **CMP-NVDA-003**.
"This is the cash flow finding. On the left is the CEO's quote, 'compute is revenue.' On the right is the follow-up, and here's the Python formula. I call it a *potential divergence*, a question for an analyst, not an accusation. The page also shows evidence that cuts the other way, like first-half cash flow still up 74%, and other explanations, like shipment timing."

## 2:15 – Research Lab
**Research Lab** tab.
"This prototype filters preloaded data. It doesn't fetch new filings or call an LLM."
1. Question: **Narrative-versus-metric analysis** → **Run Research Review** → select **CMP-NVDA-003** → challenge **Contrary evidence** → **Download research brief**.
2. Question: **Evidence gaps** → **Run Research Review** → select **CMP-NVDA-005** → challenge **Contrary evidence**.
"Here no contrary evidence is recorded. ARGUS calls that *missing evidence*, not proof there is none."

## 3:05 – Validation and honesty
**Validation** tab.
"One thing I want to be upfront about. AI helped me research the filings and build this. Inside the app, matching is a simple rule-based matcher. It isn't a trained model and makes no live AI calls. On my 12-example test it beats keyword search, 100% versus 33% precision. But that's a tiny test and I wrote the rules while looking at the same filings, so it's a sanity check, not proof. I also ran 21 automated tests, and they pass."

## 3:40 – Wrap-up (back to Dashboard)
"For Schwab, this means faster, auditable post-earnings checks and fewer errors from restated numbers. I'd measure success by analyst time saved per release and how many flagged leads analysts find useful. I haven't measured that yet. The limits: one company, public filings, a small test. Next step is swapping in an LLM matcher, tested on a much bigger set, with the same Python checks. Thank you."

---

**If asked:** *Where's the AI?* AI did the research and the build; the app itself is rule-based by design, and an LLM matcher is the next step. *Accusing NVIDIA?* No, these are research leads with counter-evidence.
**If it breaks:** `Cmd+Shift+R`. If the app won't start, record from `ARGUS_Interactive_Prototype.html` and say so.
