# ARGUS Demo Script — about 4:30 (limit 5:00)

Say it in your own words, on camera or in your own voice. **Bold = what to click.** Speak slowly; pauses are fine.

**Before recording:** `cd ~/Argus && git pull origin main && python3 -m streamlit run app.py`. Click through all 6 tabs once. Cmd+Shift+5 to record.

---

## 0:00 – The problem and how ARGUS solves it (Dashboard)
"Hi, I'm Sanskriti. This is ARGUS, built for Charles Schwab's equity research analysts.

**The problem:** after every earnings release, an analyst has to check whether what management *said* matches what the filings *show*. That's slow, and it's easy to miss things, because the wording changes every quarter and companies sometimes change their accounting, which breaks old comparisons.

**How ARGUS solves it, in three steps:**
1. It links a management statement to the filing numbers it relates to.
2. Python recalculates every figure and classifies it into one of four categories. No AI does the math.
3. It shows the full evidence trail: the quote, the source link, the formula, and evidence on both sides.

**What the AI does:** AI did the heavy lifting of gathering and cross-checking NVIDIA's six quarters of filings and building this prototype. Inside the app, the linking step is a rule-based matcher, and the numbers are plain Python, so everything is auditable."

## 0:55 – Dashboard (scroll down slowly)
"Here are the seven findings in four categories.
Latest quarter: revenue grew about 18%, but operating cash flow *fell* 52% because receivables jumped 55% to $63 billion. That's the one to ask management about.
Management guided expense growth to the 'high-30s.' Actual: 40.7% GAAP, 42.5% non-GAAP.
And NVIDIA changed its stock-comp treatment and restated old numbers: last year's Q4 expenses went from $5.1 billion to $6.7 billion. Splicing old and new data would show a fake spike."

## 1:35 – Timeline
**Timeline** tab → dropdown → **GAAP Operating Cash Flow**.
"Every number has its units, period and a link to the filing." *(Open one filing expander to show the link.)*

## 1:55 – Evidence Explorer
**Evidence Explorer** → select **CMP-NVDA-003**.
"This is the cash flow finding. On the left is the CEO's quote, 'compute is revenue.' On the right is the follow-up, and here's the Python formula. I call it a *potential divergence*, a question for an analyst, not an accusation. The page also shows evidence that cuts the other way, like first-half cash flow still up 74%, and other explanations, like shipment timing."

## 2:30 – Research Lab
**Research Lab** tab.
"This prototype filters preloaded data. It doesn't fetch new filings or call an LLM."
1. Question: **Narrative-versus-metric analysis** → **Run Research Review** → select **CMP-NVDA-003** → challenge **Contrary evidence** → **Download research brief**.
2. Question: **Evidence gaps** → **Run Research Review** → select **CMP-NVDA-005** → challenge **Contrary evidence**.
"Here no contrary evidence is recorded. ARGUS calls that *missing evidence*, not proof there is none."

## 3:20 – Validation and honesty
**Validation** tab.
"To be upfront about the AI: the matcher is simple rules, not a trained model, and there are no live AI calls. On my 12-example test it beats keyword search, 100% versus 33% precision. But it's a tiny test and I wrote the rules while reading the same filings, so it's a sanity check, not proof. I also ran 21 automated tests, and they pass."

## 3:55 – Wrap-up (back to Dashboard)
"For Schwab, this means faster, auditable post-earnings checks and fewer errors from restated numbers. I'd measure success by analyst time saved per release and how many flagged leads analysts find useful. I haven't measured that yet. The limits: one company, public filings, a small test. Next step is swapping in an LLM matcher, tested on a much bigger set, with the same Python checks. Thank you."

---

**If asked:** *Where's the AI?* AI did the research and the build; the app itself is rule-based by design, and an LLM matcher is the next step. *Accusing NVIDIA?* No, these are research leads with counter-evidence.
**If it breaks:** `Cmd+Shift+R`. If the app won't start, record from `ARGUS_Interactive_Prototype.html` and say so.
