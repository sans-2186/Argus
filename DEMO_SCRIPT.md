# ARGUS — 3-to-5 Minute Competition Presentation & Demo Script (`DEMO_SCRIPT.md`)
**Target Duration:** 4 minutes, 15 seconds (Leaves comfortable buffer under the 5:00 video limit)
**Reminder from Competition Rules:** Appear on camera or narrate in your own natural voice (do not use AI avatars or cloned voices). Show the running ARGUS app and walk through the AI verification checks.

---

## [0:00 – 0:45] 1. The Firm, The Problem & The Core Idea
**(Visual: Start on ARGUS Executive Dashboard — Tab A, showing the dark charcoal institutional interface and the 5-Step Auditable Chain banner)**

"Hi judges. Today I'm presenting **ARGUS — See Beyond the Narrative**, an AI-assisted financial research intelligence platform built for the equity research team at **Charles Schwab**.

At Charles Schwab, fundamental analysts covering mega-cap technology stocks like **NVIDIA** face a massive post-earnings synthesis challenge. Across six quarters of earnings releases and the FY2026 Form 10-K, management's narrative evolves constantly—shifting from the *'virtuous cycle of AI'* in Q3 FY26, to the *'agentic AI inflection point'* in Q4, to *'compute is revenue'* in Q2 FY27. At the same time, accounting baselines shift beneath the surface.

If an analyst uses a generic LLM chatbot to summarize filings, it risks hallucinating arithmetic or missing footnote restatements. If they use traditional keyword search, it misses paraphrased concepts entirely.

**ARGUS solves this with a strict division of labor:**
1. **AI-Assisted Semantic Discovery** connects management claims across filings even when the wording changes completely.
2. **Deterministic Python Logic** executes 100% of the numerical comparisons, ratio math, and classification rules—guaranteeing zero hallucinated numbers.

Every insight in ARGUS follows a 5-step auditable chain: **Company Statement $\rightarrow$ Original SEC/IR Source $\rightarrow$ Financial Metric $\rightarrow$ Deterministic Python Check $\rightarrow$ Analyst Finding.**"

---

## [0:45 – 1:40] 2. Live Demo: Executive Dashboard & Multi-Period Timeline
**(Visual: Scroll down Tab A to the two side-by-side Plotly charts, then click into Tab B: Narrative-vs-Metrics Timeline)**

"Let's look at what ARGUS uncovered across six authentic NVIDIA reporting periods from **Q1 FY26 through Q2 FY27** (ended July 26, 2026).

On the **Executive Dashboard**, our left chart tracks Total Revenue alongside GAAP Operating Cash Flow and Accounts Receivable. Notice that in **Q2 FY27**, revenue climbed **18% sequentially to $96.22 billion**—powered by **$89.0 billion** in Data Center revenue.

However, look at the green bars and orange line: in that exact same quarter, **Operating Cash Flow dropped 52.18% sequentially** from **$50.34 billion down to $24.08 billion**, while **Accounts Receivable surged 54.90% to $63.06 billion**.

Look at the right chart: **Operating Expenses**. In **Q1 FY27**, NVIDIA changed its Non-GAAP methodology to stop excluding Stock-Based Compensation and restated prior quarters. If a Schwab analyst splices legacy Q4 FY26 Non-GAAP OpEx (**$5,102M**) onto Q1 FY27 (**$7,449M**), their model falsely shows a **46% single-quarter expense spike** instead of the true restated **11.8% growth** from **$6,666M**.

In **Tab B (Narrative-vs-Metrics Timeline)**, analysts can toggle any metric—Revenue, Data Center, Gross Margin, Free Cash Flow, or Inventories—and inspect the exact period-by-period numbers, units, and clickable links to NVIDIA's SEC EDGAR filings."

---

## [1:40 – 2:50] 3. Deep Dive: Auditable Evidence Explorer & Finding Inspector
**(Visual: Click Tab C: Evidence Explorer & Graph. Select `CMP-NVDA-003` first, then `CMP-NVDA-001` or `CMP-NVDA-002`. Then click Tab D: Finding Inspector)**

"Let's open **Tab C: The Evidence Explorer**. Here, ARGUS renders an interactive **Evidence Relationship Graph** and displays the complete audit trail behind each comparison.

Let's select **`CMP-NVDA-003`**: *Q2 FY27 'Compute is Revenue' Narrative vs. Working Capital & Cash Flow Divergence*.
* **Box 1** shows CEO Jensen Huang's verbatim excerpt from the August 26, 2026 release: *'Its tokens are productive and profitable. Now, compute is revenue.'*
* **Box 2** pulls the Condensed Consolidated Cash Flow and Balance Sheet lines from the same filing.
* **Section 3** shows the exact Python formula executed by ARGUS: Revenue grew **+17.90% QoQ**, Operating Cash Flow contracted **-52.18% QoQ**, and Days Sales Outstanding (DSO) expanded by **14.25 days** (from **45.39 days to 59.64 days**).
* **Section 4** enforces institutional objectivity: ARGUS flags this as a **Potential narrative–metric divergence**—which is a **research lead, not an accusation of misconduct**. It automatically surfaces **Contrary Evidence** (first-half Operating Cash Flow is still up 74% YoY) and **Alternative Explanations** (Vera Rubin rack-scale shipments ramping late in Q2, creating quarter-end receivables collected in Q3).

In **Tab D (Finding Inspector)**, analysts can filter across all four competition categories:
1. **Verified numerical mismatch** (such as Q2 FY26 full-year OpEx guidance of *'high-30% range'* vs. actual FY26 10-K OpEx growth of **40.66% GAAP / 42.49% Non-GAAP**, and the **+$1,564M** Q4 FY26 Non-GAAP SBC restatement).
2. **Potential narrative–metric divergence** (the Q2 FY27 cash flow divergence and Q3 FY27's 100 bps gross margin step-down to 74.0% during the Vera Rubin ramp).
3. **No identified discrepancy** (Data Center revenue accelerating from 56% YoY to 117% YoY, and Q2 FY27's $25.78B cash shareholder return matching the ~$26.0B headline claim).
4. **Insufficient evidence** (where NVIDIA announced the new *Hyperscale* vs. *ACIE* Data Center sub-markets and the >$500B compute financing platforms, but omitted the dollar sub-market split from the press release tables).

Analysts can even use the live ingestion form at the bottom of Tab D to paste new filing excerpts and run instant verification."

---

## [2:50 – 3:45] 4. Responsible AI & Labeled Benchmark Evaluation (AI Log Walkthrough)
**(Visual: Click Tab E: Responsible AI & Benchmark Evaluation, showing the sliders, Precision/Recall metrics, and pair-by-pair table)**

"Finally, let's look at **Tab E: Responsible AI & Benchmark Evaluation**, which also covers our **AI Log**.

Why do we need semantic AI discovery instead of Ctrl+F keyword search? We built a 12-pair manually labeled test set from NVIDIA's filings (`data/evaluation_dataset.json`) and benchmarked ARGUS's **Concept-Aware Financial Semantic Engine** against an **Exact Keyword Baseline**:
* **Keyword Matching fails in two ways:** First, it misses paraphrased relationships—scoring **0.00** between *'compute is revenue'* and *'accounts receivable'*, resulting in **only 12.5% Recall**. Second, it suffers from **boilerplate false positives**—scoring **0.925 and 0.969** on completely unrelated segments (*Automotive* vs. *Professional Visualization* and *Gaming*) just because NVIDIA reuses the sentence template *'Fourth-quarter revenue was up X% from the previous quarter and up Y% from a year ago'*.
* **ARGUS's Concept-Aware Semantic Engine** maps financial concepts and penalizes cross-segment entity collisions—achieving **100% Precision, 100% Recall, and zero False Positives** on the benchmark.

In our **AI Log**, we also document three rigorous verification checks:
1. Reconciling the exact **$1,564M** Q4 FY26 Non-GAAP OpEx restatement to Note B of the Q4 reconciliation (`$1,217M` R&D SBC + `$347M` SG&A SBC).
2. Verifying FY26 10-K OpEx growth (`40.66%` GAAP vs. `'high-30%'` guidance).
3. Catching and fixing a `0.01%` floating-point rounding edge case (`-52.175%` $\rightarrow$ `-52.18%`) via our automated test suite (`tests/test_argus.py`)."

---

## [3:45 – 4:15] 5. Business Value, Limits & Conclusion
**(Visual: Return to Tab A Executive Dashboard)**

"For **Charles Schwab**, ARGUS delivers immediate business value:
* It cuts post-earnings filing reconciliation time from hours to seconds.
* It protects analysts from unadjusted Non-GAAP restatement errors.
* It surfaces high-signal fundamental research leads—like the $22.3B Q2 FY27 receivables build—before consensus catches on.

Its limits are transparent: it relies on public SEC filings, treats divergences as questions for management rather than accusations, and flags missing sub-segment tables as *Insufficient Evidence* until the full Form 10-Q is filed.

Thank you, and I look forward to your questions!"
