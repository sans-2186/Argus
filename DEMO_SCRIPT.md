# ARGUS — 5-Minute Demo Script (target 4:50, hard limit 5:00)

**Use your own voice / be on camera. No AI avatar or cloned voice.** Say it in your own words; the lines below are a guide. Numbers are from the app's data.

## Before you hit record (2 min)
1. `cd ~/Argus && git pull origin main && python3 -m streamlit run app.py` → browser at full screen, zoom ~90%.
2. Sidebar left at defaults (Reporting Period = All Periods, all 4 categories ticked).
3. Click through the 6 tabs once so nothing loads for the first time on camera.
4. Screen-record (Cmd+Shift+5, "Record Entire Screen", mic on). Close other windows/notifications.

## 0:00–0:30 · Firm, problem, idea — *Dashboard tab*
**Show:** top of Dashboard (KPI cards).
**Say:** "I'm presenting ARGUS for Charles Schwab's equity research team. After every earnings release, analysts must reconcile management's narrative against filings: wording changes between quarters, and accounting baselines quietly move. ARGUS links narrative to the numbers and runs every calculation in deterministic Python, so no arithmetic is left to an AI model. I analyzed NVIDIA's six quarters, Q1 FY26 to Q2 FY27, plus the FY26 10-K."

## 0:30–1:20 · What it found — *Dashboard tab, scroll*
**Show (scroll slowly):** the two big charts → "Findings at a Glance" row → finding cards.
**Say:**
- **Donut:** "7 findings across the four required categories: 2 verified mismatches, 2 divergences, 2 consistent, 1 insufficient evidence."
- **QoQ chart:** "Q2 FY27 revenue grew 17.9% quarter over quarter, but operating cash flow fell 52.2% while accounts receivable jumped 54.9%, to $63.1 billion."
- **Guidance chart:** "In Q2 FY26 management guided full-year operating expense growth to the 'high-30% range.' Actual FY26 GAAP growth was 40.66% and non-GAAP 42.49%, so it's above the guided ceiling."
- **OpEx chart:** "In Q1 FY27 NVIDIA stopped excluding stock comp from non-GAAP and restated prior quarters. Q4 FY26 non-GAAP OpEx went from $5,102M to $6,666M, +$1,564M. A model that splices old and new series would be wrong."

## 1:20–1:50 · Timeline tab
**Click:** `Timeline` tab → dropdown "Select Primary Financial Metric" → **GAAP Operating Cash Flow ($ in millions)**.
**Show:** the line, then the table (units and Filing URL columns), then point at the **collapsed** filing expanders; open one to show the SEC link.
**Say:** "Every number carries units, period, and a link to the filing."

## 1:50–2:30 · Evidence Explorer
**Click:** `Evidence Explorer` tab → selectbox → **CMP-NVDA-003 … [Potential narrative–metric divergence]**.
**Show, in order:** relationship graph → left box (CEO quote, Aug 26, 2026) → right box → "Deterministic Python Calculation" code block → right column.
**Say:** "The quote is 'compute is revenue.' The Python formula shows revenue +17.90%, cash flow −52.18%, a 70-point gap. This is classified a *potential divergence*, a research lead, not an accusation. The record also lists contrary evidence: first-half operating cash flow is still up 74% year over year, and alternative explanations like late-quarter Vera Rubin shipment timing."

## 2:30–3:40 · Research Lab (new)
**Click:** `Research Lab` tab. **Say first:** "This prototype filters preloaded data. It doesn't fetch new filings or call an LLM."
1. Question = **Narrative-versus-metric analysis** → click **Run Research Review** → point at the two charts → select **CMP-NVDA-003** → show original/follow-up excerpts with dates and links → Analyst challenge = **Contrary evidence** (two items appear) → click **Download research brief (.md)** (show it downloaded; optionally open it for 3 seconds).
2. Question = **Evidence gaps** → **Run Research Review** → select **CMP-NVDA-005** → challenge = **Contrary evidence**.
**Say on #2:** "Here the record has no contrary evidence listed. ARGUS says that's *missing recorded evidence, not proof none exists*. It never turns an empty list into a conclusion."
*(If short on time: skip #2's charts talk; skip accounting-methodology question. Mention it's available.)*

## 3:40–4:20 · Validation + AI honesty
**Click:** `Validation` tab (sidebar status is visible too).
**Show:** the sentence "Local concept-aware matching active. No live Gemini inference…" → benchmark metrics → pair table.
**Say:** "I want to be precise about the AI. AI did the research and build work: gathering and cross-checking the filings and building the prototype. Inside the app, matching is a transparent local rule-based matcher plus deterministic Python. It's not a trained model and makes no live LLM calls. On my 12-pair labeled set it scores 100% precision and recall versus keyword matching's 33% precision and 12.5% recall at the default threshold. But 12 pairs is tiny and I wrote the concept ontology while looking at the same filings, so treat it as a sanity check, not proof it generalizes. I ran 21 automated tests, which pass, and reconciled the $1,564M restatement to the SBC footnote exactly."

## 4:20–4:50 · Value, limits, next steps — *back on Dashboard*
**Say:** "Value: faster, auditable post-earnings reconciliation for analysts, and catching things like the restatement that break time-series models. *(Assumption: time savings are not measured here.)* I'd measure success by analyst review time per earnings release and the share of flagged leads analysts judge useful. Limits: one company, public filings only, small benchmark. Next step: replace the local matcher with an LLM or embedding model, evaluated on a much larger labeled set, with the same Python verification layer. Thank you."

## If a judge asks (Final round Q&A)
- **"Where is the AI in the app?"** → "The AI did the filing research and cross-checking and built the prototype. In the running app, matching is rule-based and calculations are deterministic by design. LLM/embedding matching is the next step, and it'd be benchmarked against this baseline."
- **"Is 100% on your benchmark meaningful?"** → "Only as a sanity check. 12 pairs, ontology written with the same filings in view."
- **"Are you accusing NVIDIA of something?"** → "No. These are research leads, each with contrary evidence and alternative explanations."
- **"Why deterministic Python for math?"** → "Auditability: every figure shows its formula and inputs."

## Quick fixes if something breaks on camera
- Blank chart → `Cmd+Shift+R`. Streamlit error → stop the recording, restart `streamlit run`, re-record that section.
- Can't get pyarrow/numpy working → record the section from the repo's `ARGUS_Interactive_Prototype.html` (static version) and say so.
