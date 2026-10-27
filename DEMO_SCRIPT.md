# ARGUS Demo Script — about 4:30 (limit 5:00)

Say it in your own words, on camera or in your own voice. **Bold = click.** 👉 = where to point. Move the cursor slowly and rest on each item for a second.

**Before recording:** `cd ~/Argus && git pull origin main && python3 -m streamlit run app.py`. Click through all 6 tabs once. Cmd+Shift+5 to record.

---

## 0:00 – The problem and how ARGUS solves it (Dashboard tab)
👉 Header bar "ARGUS — See Beyond the Narrative" → the 5 KPI cards → the one-line "Audit chain" caption under them.

"Hi, I'm Sanskriti. This is ARGUS, built for Charles Schwab's equity research analysts.

**The problem:** after every earnings release, an analyst has to check whether what management *said* matches what the filings *show*. That's slow and easy to get wrong, because the wording changes every quarter and companies sometimes change their accounting, which breaks old comparisons.

**How ARGUS solves it, in three steps:**
1. It links a management statement to the filing numbers it relates to.
2. Python recalculates every figure and classifies it into one of four categories. No AI does the math.
3. It shows the full evidence trail: the quote, the source link, the formula, and evidence on both sides.

**What the AI does:** AI did the heavy lifting of gathering and cross-checking NVIDIA's six quarters of filings and building this prototype. Inside the app, the linking step is a rule-based matcher, and the numbers are plain Python, so everything is auditable."

## 0:55 – Dashboard (scroll down slowly)
👉 **Left chart** ("Revenue, Operating Cash Flow & Receivables"): last group, Q2 FY27. The green bar drops while the orange line shoots up.
👉 **Right chart** ("Operating Expenses"): the dotted blue line jumping in Q1 FY27, then the purple restated line beside it.
👉 **"Findings at a Glance" row:** donut center number (7) → middle chart, last group (revenue up, cash flow down, receivables up) → right chart: gray ceiling bar and dashed line, then the two red bars above it.
👉 **Finding cards:** red-bordered cards (mismatches), then amber ones (divergences).

"Here are the seven findings in four categories.
Latest quarter: revenue grew about 18%, but operating cash flow *fell* 52% because receivables jumped 55% to $63 billion. That's the one to ask management about.
Management guided expense growth to the 'high-30s.' Actual: 40.7% GAAP, 42.5% non-GAAP.
And NVIDIA changed its stock-comp treatment and restated old numbers: last year's Q4 expenses went from $5.1 billion to $6.7 billion. Splicing old and new data would show a fake spike."

## 1:35 – Timeline *(cut this first if you're over time)*
**Timeline** tab → dropdown → **GAAP Operating Cash Flow**.
👉 The dropdown and line chart → scroll to the table: "Units" and "Filing URL" columns → under "Source Filings," **open one filing** and point at the SEC link.

"Every number has its units, period and a link to the filing."

## 1:55 – Evidence Explorer
**Evidence Explorer** tab → select **CMP-NVDA-003**.
👉 The 5-node graph, left to right → left box (CEO quote) → right box (follow-up and date) → the formula code block → right column: "Contrary / Mitigating Evidence" and "Alternative Explanations."

"This is the cash flow finding. On the left is the CEO's quote, 'compute is revenue.' On the right is the follow-up, and here's the Python formula. I call it a *potential divergence*, a question for an analyst, not an accusation. The page also shows evidence that cuts the other way, like first-half cash flow still up 74%, and other explanations, like shipment timing."

## 2:30 – Research Lab
**Research Lab** tab.
👉 The blue note at the top ("Prototype scope… does not call an LLM").

"This prototype filters preloaded data. It doesn't fetch new filings or call an LLM."

**Run 1:** question **Narrative-versus-metric analysis** → **Run Research Review**.
👉 The two charts (scores per finding, findings by classification) → "Select a finding" dropdown: **CMP-NVDA-003** → the two excerpt boxes (dates, links) → metric block on the left, classification on the right.
**Analyst challenge** → **Contrary evidence** (👉 the radio buttons) → **Download research brief (.md)** (👉 the button).

**Run 2:** question **Evidence gaps** → **Run Research Review** → select **CMP-NVDA-005** → challenge **Contrary evidence**.
👉 The line saying no contrary evidence is recorded.

"Here no contrary evidence is recorded. ARGUS calls that *missing evidence*, not proof there is none."

## 3:20 – Validation and honesty
**Validation** tab.
👉 Grey caption under the title: "Local concept-aware matching active. No live Gemini inference…" (also in the left sidebar) → the 4 metric tiles (precision, recall, F1, false positives) → the comparison table below them.

"To be upfront about the AI: the matcher is simple rules, not a trained model, and there are no live AI calls. On my 12-example test it beats keyword search, 100% versus 33% precision. But it's a tiny test and I wrote the rules while reading the same filings, so it's a sanity check, not proof. I also ran 21 automated tests, and they pass."

## 3:55 – Wrap-up
Back to the **Dashboard**; rest the cursor on the donut or the finding cards.

"For Schwab, this means faster, auditable post-earnings checks and fewer errors from restated numbers. I'd measure success by analyst time saved per release and how many flagged leads analysts find useful. I haven't measured that yet. The limits: one company, public filings, a small test. Next step is swapping in an LLM matcher, tested on a much bigger set, with the same Python checks. Thank you."

---

**If asked:** *Where's the AI?* AI did the research and the build; the app itself is rule-based by design, and an LLM matcher is the next step. *Accusing NVIDIA?* No, these are research leads with counter-evidence.
**If it breaks:** `Cmd+Shift+R`. If the app won't start, record from `ARGUS_Interactive_Prototype.html` and say so. Zoom the browser in (`Cmd +`) once if charts are hard to read.
