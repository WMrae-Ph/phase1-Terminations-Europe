# Project log

Decisions are recorded with date and rationale, so the analysis stays traceable.

## 2026-10-27 – Block 1: Project setup and analysis decisions

| ID | Decision | Rationale |
|---|---|---|
| D01 | Data sources: only ClinicalTrials.gov, EudraCT (EU CTR) and CTIS | Focus and reproducibility |
| D02 | ClinicalTrials.gov via API v2; manual CSV exports used only as a cross-check | API provides `whyStopped`, `healthyVolunteers`, arm types, site countries and MeSH terms; one query across all countries avoids duplicates |
| D03 | Countries: UK, DE, FR, ES, NL, BE, IT | Major European Phase I sites |
| D04 | Study type interventional; Phase 1 and Phase 1/2; **Early Phase 1 excluded** | Early Phase 1 (Phase 0) is a different study type |
| D05 | Study start 2005–2022 | Earlier: too few registrations; later: often no final status yet |
| D06 | Outcome: Completed = 0, Terminated = 1; Withdrawn and open/unknown statuses excluded | Withdrawn trials never enrolled participants; open statuses have no outcome |
| D07 | Termination reason categories: Safety, Efficacy/Futility, Recruitment, Funding, Strategic/Business, Other, Not stated. Multi-label allowed; additionally **one primary reason per trial** for figures | Free-text reasons often name several causes |
| D08 | Rule-based reason classification with negation handling, validated manually by a domain expert (pharmacist) | Transparent and auditable |
| D09 | Pre/post comparison: 2005–2015 vs. 2017–2022; 2016 excluded as transition year | BIA 10-2474 incident in January 2016 |
| D10 | Timeline markers: EMA first-in-human guideline 2007 and revision 2017 (effective 2018) | Regulatory responses to TGN1412 and BIA 10-2474 |
| D11 | Healthy-volunteer trials as a dedicated subgroup throughout | Both incidents involved healthy volunteers |
| D12 | Actual enrollment and other post-start information excluded from the main model | Data leakage: terminated trials report lower actual enrollment |
| D13 | Modelling: stratified CV, `class_weight='balanced'`, PR-AUC as primary metric | Strong class imbalance |
| D14 | CTIS and EudraCT used descriptively only (no model training) | Limited / selective data |
| D15 | EudraCT export limited to max. 2 work blocks; otherwise continue with a smaller sample | Time budget |
| D16 | Raw registry exports not committed; processed data + download instructions are | Size and terms of use |
| D17 | License: MIT | Standard open-source license |
| D18 | Work environment: Claude Code (local Python virtual environment, notebooks executed with nbconvert); publication channel decided in Phase 7 | Change from original Colab/GitHub setup |

### Environment notes (Block 1)
- Network check: `clinicaltrials.gov`, `www.clinicaltrialsregister.eu` and `euclinicaltrials.eu`
  were initially **blocked** by the session's network policy (HTTP 403 at proxy level).
  After enabling the domains, all three registries are reachable (HTTP 200).
  ClinicalTrials.gov API version 2.0.5, data timestamp 2026-10-27T09:00:04.
- API test query (interventional, Phase 1 incl. Phase 1/2, any of the 7 countries, all years
  and statuses): **11,120** unique trials; Germany alone: 3,157 (manual CSV: 3,154).

## 2026-10-27 – Block 2: ClinicalTrials.gov download and input checks (notebook 01, Part A)

- Downloaded 11,120 / 11,120 records (23 MB compressed); 0 duplicate NCT IDs.
- Phases: Phase 1 8,069; Phase 1/2 3,051; Early Phase 1 0 (not matched by the query).
- 6 trials matched the location text search but have no site in a target country →
  flagged `in_target_countries = False`, to be excluded in notebook 02 (**D19**).
- Per-country counts deviate ≤ 0.3 % from the manual CSV exports → API data confirmed.
- `why_stopped` filled for 89 % of terminated trials.
- Condition MeSH terms missing for 30 % of trials (52 % of healthy-volunteer trials, which
  often list "Healthy" as condition) → indication grouping needs a free-text fallback (**D20**).
- Preview (not final, see notebook 02): start 2005–2022 and status Completed/Terminated →
  ~7,960 trials, ~14.5 % terminated, ~47 % in healthy volunteers.

## 2026-10-27 – Block 3: EudraCT / EU CTR download (notebook 01, Part B)

- Export method: page-wise plain-text download "Full Trial Details"
  (`/ctr-search/rest/download/full?query=&phase=phase-one&page=N&mode=current_page`),
  20 trials per page, 142 pages, pause 1.5 s, retries; ~50 min. Completed in **one** block.
- 2,823 / 2,823 trials (complete); 6,083 country records.
- Status values found in addition to the expected ones: "Trial now transitioned" (to CTIS),
  "Suspended by CA", empty status fields.
- **D21** – one status per trial by priority rule: Prematurely Ended > Temporarily Halted /
  Suspended > Ongoing / Restarted > Transitioned to CTIS > Completed > GB – no longer in EU/EEA
  > Not authorised > Not reported > Outside EU/EEA. `status_mixed` flag for 583 trials.
- Result: Completed 1,264 · Prematurely Ended 591 · Ongoing 370 · Transitioned 264 ·
  Outside EU/EEA 195 · GB hidden 89 · Halted 30 · Not reported 17 · Not authorised 3.
- Transparency finding: only **4** adult non-PIP Phase-I-only trials are visible
  (vs. 1,761 adult non-PIP Phase I/II trials).
- No termination reason in EU CTR protocol data.
- Preview for Block 19: 5,378 ClinicalTrials.gov trials carry a EudraCT number, but only
  850 EudraCT numbers appear in the EU CTR Phase I download.
- **D22** (for Block 18, requested at sign-off of Block 3): in addition to the priority rule
  D21, compute a strict variant "Prematurely Ended in **all** countries with a reported
  status", to show how strongly the termination share depends on the definition.
- Spot check via a ClinicalTrials.gov search connector: Germany, interventional, Phase 1,
  status Terminated → **333** trials (all years; Phase 1/2 included). Consistent with the
  earlier API sample (332).

## 2026-10-28 – Block 4: CTIS download (notebook 01, Part C)

- Export method: JSON interface of the public portal – `POST /ctis-public-api/search`
  (all trials, page size 500) and `GET /ctis-public-api/retrieve/{ctNumber}` (full record).
  The search returns max. 10,000 records per query → two queries (sorted ASC and DESC by
  trial number), combined by trial number: 12,725 / 12,725 trials.
- Phase I selection (**D23**): portal phase text "Human Pharmacology (Phase I)" or
  "Phase I and Phase II (Integrated)" → 3,522 trials; full records downloaded for all.
- Status codes translated with the portal's own label list (1–12); mapping to
  ClinicalTrials.gov statuses in `mappings/ctis_status_mapping.csv` (**D24**).
  "Ended" is split by the member-state event `EARLY_TERMINATION`: any country → TERMINATED
  (strict variant: all countries, analogous to D22).
- Ended: 1,603; early termination in ≥ 1 country 441 (27.5 %), in all countries 360 (22.5 %).
- Coded early-termination reasons (trials with early termination in ≥ 1 country, any status, n = 536;
  several codes possible): Sponsor decision 429 (80.0 %), Feasibility 57, Safety 17, others 44.
  *(Denominator added in Block 19, see D64.)*
- Transitioned from EudraCT: 952 Phase I trials; 528 of them were not in the EU CTR Phase I
  download (i.e. previously not public as Phase I trials).
- Early termination: transitioned 43 % vs. new 22 %; patients 51 % vs. healthy volunteers 8 %
  (descriptive; to be interpreted in Block 19).
- CTIS remains descriptive only (D14).
- **D25** (for Block 19, requested at sign-off of Block 4): the CTIS comparison healthy
  volunteers (8 %) vs. patient trials (51 %) is only shown together with the explanation of
  right-censoring (young data; regular – often longer – patient trials frequently still
  running), never on its own.

## 2026-10-28 – Block 5: Analysis set ClinicalTrials.gov (notebook 02, Part A)

- Flow: 11,120 → −6 no target-country site → −33 no start date → −331 start < 2005 →
  −1,674 start > 2022 → −1,116 status not Completed/Terminated → **7,960** trials
  (saved: `data/processed/flow_counts_ctgov.csv`, `figures/01_flow_diagram.png`).
- Outcome: 1,154 terminated (14.5 %). Crude by period: pre 10.1 %, 2016 12.7 %, post 22.1 %.
- Right-censoring: share still running by start year < 2 % (≤ 2015), 11 % (2019),
  15 % (2020), 19 % (2021), 29 % (2022) → **D26**: sensitivity analyses with start year
  ≤ 2019 and ≤ 2020 in Block 14; crude pre/post difference not interpreted on its own.
- Status UNKNOWN similar across periods (4.9 / 5.9 / 5.4 %).
- Shared figure style `notebooks/viz_style.py` (validated categorical palette, light mode).

## 2026-10-28 – Terms of use check (after Block 5)

- **D27**: wording for CTIS access set to "public search interface, not a documented API"
  (limitations, raw-data README, notebook 01). Terms of use checked and recorded in
  `docs/data_sources_and_terms.md`: euclinicaltrials.eu has no own terms; EMA Legal Notice
  applies (reuse allowed incl. commercial, with EMA acknowledged as source; third-party
  content excluded). EU CTR disclaimer requires attribution "EU Clinical Trials Register" +
  access date. All figures will carry source + access date. ClinicalTrials.gov terms to be
  checked in Phase 7.

## 2026-10-28 – Flow diagram v2 and Block 6: Features part 1 (notebook 02, Part B)

- Flow diagram: outcome boxes (Completed 6,806 / Terminated 1,154), first exclusion renamed
  "No site listed in UK, DE, FR, ES, NL, BE or IT (location search text match only)".
- Features derived (see `docs/data_dictionary.md`) with leakage classification ✅ / ⚠️ / ❌.
- **D28**: post-start information excluded from the model: actual enrollment,
  registration after primary completion (10.6 % of completed vs. 2.7 % of terminated →
  selective retrospective registration), results posted. Sensitivity analysis without
  retrospectively registered trials planned (Block 14/16).
- **D29**: site/country counts (⚠️) kept in the main model; sensitivity model without them.
  Site status (withdrawn sites) is not available for ended trials.
- Placebo = PLACEBO_COMPARATOR arm or "placebo" in intervention/arm name: 2,202 (27.7 %).
- Univariate: healthy volunteers 6.5 % vs. patients 21.5 % terminated (whole period
  2005–2022).
- **D30** (for Block 15, requested at sign-off of Block 6): check correlations between
  features (e.g. healthy volunteers, crossover, randomisation, Phase 1/2, multinational)
  before interpreting logistic-regression coefficients (collinearity → unstable estimates).

## 2026-10-28 – Block 7: Indication groups (notebook 02, Part C)

- **D31**: 9 indication groups (`mappings/condition_groups.csv`), assigned by MeSH terms +
  ancestors with priority order (Oncology > Infectious > Nervous system > Cardiovascular >
  Metabolic > Immunology > Respiratory > Other), free-text fallback, healthy-volunteer rule,
  documented overrides (`mappings/condition_group_overrides.csv`).
- Sources: MeSH 64 %, healthy-volunteer rule 23 %, free text 9 %, overrides 4 %,
  unclassified → Other 1 %.
- Fix: infectious keyword "hepatitis" no longer matches "steatohepatitis" (NASH).
- Borderline cases B1–B10 written to `validation/condition_groups_borderline_review.csv`;
  **pending domain-expert decision** (current assignments are preliminary).
- Analysis dataset saved: `data/processed/ctgov_analysis_dataset.parquet` (7,960 × 83).
- **Borderline cases decided** (domain expert, 28 Oct 2026): all B1–B10 kept as recommended;
  decisions in `validation/condition_groups_decisions.csv`. Expert notes:
  - B3/B4: consistent with **ATC group N** (nervous system: incl. analgesics, anaesthetics,
    psycholeptics/psychoanaleptics).
  - B8: MDS, myelofibrosis/MPN and mastocytosis are **myeloid neoplasms (WHO classification)**.
  - B10: NAFLD/NASH were renamed **MASLD/MASH** (metabolic dysfunction-associated) in 2023;
    new terms added to the override pattern.
  → Indication groups are **final**.
- **D32** (for Blocks 11–14, requested at sign-off of Block 7): oncology is one third of the
  dataset, has 26 % terminations and only 3 % healthy volunteers → the comparison healthy
  volunteers vs. patients is additionally shown **excluding oncology**, to check that the
  difference is not just an oncology effect.

## 2026-10-28 – Block 8: Classification of termination reasons (notebook 03)

- Rule-based classifier, 61 patterns (`mappings/why_stopped_keywords.csv`), 31 assertion
  tests documenting negation handling and multi-label behaviour.
- Negation logic (**D33**): keyword ignored if a negation cue precedes it in the same clause,
  unless a causal connector (due to, because, based on, for, since, …) follows other words
  after the cue; "non-clinical" / "non-favorable" normalised (not negations); clauses split at
  . ; ! ? and ": " (not at "risk:benefit").
- Primary reason priority (**D34**, proposal): Safety > Efficacy/Futility > Recruitment >
  Funding > Strategic/Business > Sponsor decision (unspecified) > Other > Not stated.
- "Sponsor decision (unspecified)": decided 29 Oct 2026 → own category (see D36).
- Result (before validation): Safety primary reason 137 / 1,154 (11.9 %); unmatched texts
  65 (5.6 %); 155 texts with ignored negated mentions (143 negated safety mentions).

## 2026-10-29 – Decisions after Block 8 and preparation of Block 9

- **D34 confirmed**: primary-reason priority accepted.
- **D35**: **COVID-19** as own category (28 trials named the pandemic; 19 of them had been in
  "Other", 5 in Recruitment, 4 in Strategic/Business). Placed in the priority after
  Efficacy/Futility and before Recruitment (pandemic usually the root cause of recruitment or
  business problems): Safety > Efficacy/Futility > COVID-19 > Recruitment > Funding >
  Strategic/Business > Sponsor decision (unspecified) > Other > Not stated.
- **D36**: "Sponsor decision (unspecified)" kept as **own category** (98 trials) – makes the
  transparency gap visible and is comparable with the CTIS code "Sponsor decision".
- "Other" reviewed (179 trials as primary reason): unmatched 65, planned stop after a study
  part 23, drug supply 21, objectives met early 20, regulatory 11, operational/design/site/
  administrative ~23, PK/interim/stopping rules/DMC ~19.
- **D37**: validation **blinded** and **stratified**: all 137 Safety texts (stratum S),
  all 21 ambiguous-flag texts (A), random 60 of 865 other texts (R, seed 2026, weight 14.42);
  131 empty texts excluded (Not stated by definition). Review workbook shows only ID, NCT ID
  and text, rows shuffled; key stored separately. Precision/recall computed with sampling
  weights (inverse inclusion probabilities) in Block 10.
- **D38** (for Block 14): sensitivity analysis excluding COVID-19-related terminations
  (4.4 % of terminations of trials started 2017–2022).
- **D35 confirmed** (29 Oct 2026): final primary-reason priority Safety > Efficacy/Futility >
  COVID-19 > Recruitment > Funding > Strategic/Business > Sponsor decision (unspecified) >
  Other > Not stated. Blinded review in progress (domain expert).
- Review coding (29 Oct 2026): the expert fills in the review in Apple Numbers (no drop-down
  support) using short codes – primary: S Safety, E Efficacy/Futility, C COVID-19,
  R Recruitment, F Funding, B Strategic/Business, D Sponsor decision (unspecified), O Other,
  N Not stated; safety_related: y/n; other categories: codes separated by ';'. Importer
  `notebooks/review_import.py` converts codes (or full names, case-insensitive) and reports
  every invalid/missing entry by review_id; tested on a synthetic file.

## 2026-11-01 – Block 10 (part 1): Validation of the termination-reason classifier

- Expert review received (Apple Numbers, short codes) → exported with `numbers-parser` to
  `validation/why_stopped_review_expert_filled.csv`. All 218 rows valid after normalisation
  (whitespace, case, diacritics e.g. "Ń" → N); NCT IDs unchanged; 2 texts changed only in
  capitalisation (Numbers autocorrect, rows 54 and 85). 11 texts marked "ambiguous".
- Review sample frozen: notebook 03 no longer regenerates workbook/key if they exist.
- **Results v1 (out-of-sample, weighted):** primary-reason agreement 83.9 % (unweighted
  79.8 %), Cohen's kappa 0.80 (0.69); Safety precision 78.1 % (95 % CI 70.5–84.2 %), Safety
  recall 100 % in sample, lower 95 % bound 66 % (Clopper–Pearson on 0/21 and 0/60 misses).
- Validated estimate of safety-related terminations: **107 / 1,154 (9.3 %)**, upper bound
  162 (14.0 %); algorithm v1: 137 (11.9 %).
- Main error: "safety" mentioned as information (profile characterised, data sufficient,
  safety follow-up) – 18 of 30 Safety false positives.
- COVID-19 not represented in the random part of the sample → not validated.
- Builder scripts of the notebooks restored from the backup after the session's temporary
  folder was reset; now kept in a separate working folder outside the repository (copies in the backups under `_working_files/builders`).

## 2026-11-01 – Block 10 (part 2): Rule version v2, hold-out check, final-label decision

- Decisions by the domain expert: A (rule revision) accepted; point 5 specified:
  "recruitment … lower than anticipated" → Recruitment, "not further develop" →
  Strategic/Business, only "trial never commenced" → Not stated. B (blinded hold-out check incl.
  all COVID-19 texts) accepted. C2 accepted.
- **D39 – rule version v2**: (1) generic safety/tolerability/benefit-risk wording used as
  information (characterised, sufficient, collected, follow-up, unchanged, improve …) is not a
  reason; (2) negation reaches across termination words ("not terminated due to a safety
  reason"); (3) benefit-risk = Safety unless used as information – **adapted** from the
  proposal "only with negative direction", because the expert had classified neutral wording
  such as "terminated based on benefit-risk profile assessment" as Safety (the stricter rule
  would have removed correct hits); (4) "no … efficacy" with ≤ 1 qualifier; (5) point-5 rules.
  v1 frozen: `mappings/why_stopped_keywords_v1.csv`, `data/processed/why_stopped_classified_v1.parquet`.
- v1 → v2: primary reason changed for 29 trials (23 inside, 6 outside the validation sample);
  Safety (multi-label) 137 → 118. On the validation sample (optimistic): weighted agreement
  90.9 % (v1 83.9 %), kappa 0.89 (0.80), Safety precision 90.7 % (v1 78.1 %), no Safety case lost.
  **Official accuracy remains v1.**
- **D40 – hold-out check**: blinded workbook `validation/why_stopped_holdout_blinded.xlsx` with
  the 6 changed trials outside the sample + all 28 COVID-19 texts (34 texts, shuffled; key
  separate, frozen).
- **D41 – final labels (C2)**: expert label where reviewed (218 + 34 hold-out texts), otherwise
  algorithm v2 ("expert-adjudicated where available"); documented per trial with a source column.
- **README to-do**: mention the uncertainty of the non-Safety categories, e.g.
  Efficacy/Futility 9.4 % (algorithm v1) vs. 15.3 % (weighted expert estimate), because these
  estimates rest on 60 random texts (weight 14.4 each).

## 2026-11-02 – Block 10 (part 3): Hold-out results, final labels, second-rater sample

- Benefit-risk rule as implemented in D39 confirmed by the expert ("matches my rating logic").
- **D42 – coding rule column E for COVID-19 texts** (expert): only safety of the investigational
  product counts as "yes"; pandemic-related terminations are "no".
- Hold-out review (Numbers, short codes) exported to `validation/why_stopped_holdout_expert_filled.csv`;
  34/34 rows valid, NCT IDs and texts unchanged.
- **v2 on new data – only 6 texts (to be reported cautiously):** expert agreed with v2 in 4,
  with v1 in 2 cases. Too small for an accuracy estimate; no gross errors introduced by v2.
- Consistency check: identical wording "sponsor decided not to continue development of certain
  treatment combinations" was labelled Strategic/Business (main review, ID 156) and Sponsor
  decision (hold-out, ID 23) → genuine borderline case; **open question to the expert**.
- COVID-19 precision 25/28 = 89.3 % (95 % CI 72.8–96.3 %). Hold-out ID 5 ("risk of COVID-19
  infection at study site visits … unacceptable patient safety risk") labelled Safety / yes –
  **open question**: consistent with D42 (pandemic-related → no)?
- **Final labels (D41)**: expert 252 (218 + 34), algorithm v2 902 →
  `data/processed/why_stopped_final.parquet`. Safety-related: 108 / 1,154 (9.4 %).
- **D43 – second rater**: blinded workbook `validation/why_stopped_second_rater_blinded.xlsx`
  (50 of the 218 main-review texts, stratified by the first expert's category, shuffled; key
  separate and excluded from backups). Inter-rater kappa to be computed if a second rater is found.

## 2026-11-04 – Block 10 closed: expert corrections, final labels, reliability

- Expert answers to the open queries: **a)** the wording "sponsor decided not to continue
  development of certain treatment combinations" → **Strategic/Business** for all 3 trials
  (main review 156, hold-out 23, 24): a reason is given (development discontinued), therefore
  not "Sponsor decision (unspecified)". **b)** hold-out ID 5 → **COVID-19 / no** per D42,
  comment "participant safety (COVID)".
- Corrected main review received (`why_stopped_review_blinded_3`, 4 Nov 2026), exported to
  `validation/why_stopped_review_expert_filled_corrected.csv` (original export kept). Diff
  against the first version: **ID 173** Other/no → Safety/yes (D39, benefit-risk as reason);
  **ID 169** Other/no → Safety/yes, comment "ambiguous" kept (termination criteria during dose
  escalation). **ID 174** was already Other/no in the first version – no change needed.
- All corrections listed in `validation/why_stopped_expert_corrections.csv` (K1–K10).
  Metrics reported as blinded and after correction (v1 Safety precision 78.1 % → 78.8 %).
- **Final labels updated (D41)**: Safety-related terminations **109 / 1,154 (9.4 %)**, i.e.
  1.4 % of all 7,960 trials in the analysis set.
- **D44 – reliability**: no second rater. The 50-text "second rater" workbook was re-rated by
  the expert herself after a few days → **intra-rater (test-retest) reliability** only, using
  the ORIGINAL re-rating before correction; the corrected re-rating
  (`validation/why_stopped_retest_corrected_documented.csv`) is kept as documented re-assessment
  only. The original file ("why_stopped_retest_ORIGINAL_vor_Korrektur") **has not been received
  yet** → test-retest pending. No inter-rater kappa.
- Blank template kept for a possible future second rater:
  `validation/templates/why_stopped_second_rater_TEMPLATE_blank.xlsx` (key unchanged, excluded
  from backups).

## 2026-11-04 – Block 11: Descriptive analysis part A (notebook 04)

- 95 % CIs: Wilson score interval for all shares (**D45**).
- Overall: 1,154 / 7,960 terminated = 14.5 % (13.7–15.3). Safety-related terminations 109 =
  9.4 % of terminated (7.9–11.3) = 1.4 % of all trials (1.1–1.6).
- Strategic/business 26.1 %, no reason stated 12.4 %, sponsor decision without reason 8.5 %
  (together 47 %). Efficacy/Futility uncertainty (algorithm 9.4 % vs. weighted expert 15.3 %)
  stated in the notebook text.
- D32 applied: healthy volunteers vs. patients terminated 6.5 % vs. 21.5 % (all) and 6.4 % vs.
  13.8 % (excluding oncology) → not only an oncology effect. Safety-related terminations 0.9 % vs.
  1.8 % (all) but 0.9 % vs. 1.0 % (excluding oncology) → safety difference essentially an
  oncology effect. Robust for start 2005–2019.
- Figures: `figures/02_termination_reasons.png`, `figures/03_healthy_volunteers_vs_patients.png`
  (title worded neutrally to reflect the safety result outside oncology).

## 2026-11-05 – Test-retest (intra-rater) reliability

- Original re-rating received ("why_stopped_retest_ORIGINAL_vor_Korrektur") → exported to
  `validation/why_stopped_retest_original.csv`; 50/50 rows valid, NCT IDs and texts unchanged.
- Compared with the expert's original main-review labels (both as first given, before any
  correction): primary reason agreement **84.0 %**, Cohen's kappa **0.78** (bootstrap 95 % CI
  0.65–0.91); safety yes/no kappa **0.96** (98 % agreement). Results:
  `validation/why_stopped_retest_results.csv`.
- The corrected re-rating differs from the original in 9 primary and 2 safety labels – kept as
  documented re-assessment only, not used for reliability (D44).

## 2026-11-05 – Block 12: Descriptive analysis part B (notebook 04)

- Small groups (< 100 trials) flagged; 95 % Wilson CIs throughout (D45).
- **D46 – country counting**: trials with sites in several target countries are counted in each
  country (11,092 country rows for 7,960 trials), clearly labelled; single-country trials
  shown for comparison (each trial counted once).
- Indication: oncology 26.0 % terminated, healthy volunteers without target disease 5.2 %;
  safety-related highest in oncology (2.3 %), other groups 0.2–1.7 % (overlapping CIs).
- Country: IT/ES/FR high with multi-country counting (27/26/22 %), single-country trials
  6.5–15.8 % → differences mainly reflect trial mix (share of healthy-volunteer and multinational
  oncology trials), not national performance.
- Sponsor: crude industry 14.8 % vs. academic 13.7 %; patient trials 23.4 % vs. 16.8 %;
  healthy-volunteer trials 6.4 % vs. 7.1 %; government/network group small (76).
- Start year: descriptive only (D26); 8–13 % (2005–2016), rising from 2017 (18 %) to ~25 %
  (2020–2021); safety-related 0.5–2.4 % per year without a visible change around 2016.
  Adjusted pre/post comparison and sensitivity analyses in Blocks 13–14.
- Figures: `04_terminations_by_indication.png`, `05_terminations_by_country.png`,
  `06_terminations_by_start_year.png` (markers TGN1412 2006, FIH guideline 2007, BIA 10-2474 2016,
  revised FIH guideline 2017/2018; years ≥ 2019 shaded as still maturing).
- **D47 – README wording** (expert, 5 Nov 2026): the reliability is to be called
  "**test-retest reliability of a single expert rater**" (not inter-rater reliability).

## 2026-11-05 – Block 13: Pre/post 2016 comparison (notebook 05)

- Notebook 02 refactored: features are now computed for all 9,076 trials started 2005–2022
  (`data/processed/ctgov_window_dataset.parquet`); the analysis dataset is verified to be
  identical row by row (7,960 × 83).
- **D48 – models**: logistic regression, OR post (2017–) vs. pre (2005–2015), 2016 excluded;
  step-wise M0 crude → M1 + trial mix (indication, healthy volunteers, Phase 1/2) → M2 + design &
  sponsor (randomised, blinded, placebo, biological, sponsor type) → M3 + ⚠️ site features
  (multinational, log sites). Outcome (b) safety-related: parsimonious model (post, oncology,
  healthy volunteers, Phase 1/2) plus Firth penalised regression.
- **D49 – fixed observation window**: all started trials (any status, without Withdrawn),
  start ≤ 2020, outcome = terminated within 3 years (1,096 days) after start (end date = actual
  completion, fallback primary completion); running/unknown = not terminated within 3 years.
  Prepared here (Block 13) and reusable for Block 14.
- **D38 applied**: COVID-19-related terminations removed as sensitivity analysis.
- Results (a): crude OR 2.53 (2.22–2.88); adjusted 2.67–2.85 → not explained by trial mix;
  3-year window OR 1.75 (1.46–2.10), adjusted 1.69–1.84; without COVID hardly changed.
- Results (b): A OR 1.60 (1.08–2.35), Firth identical; window B OR 1.48 (0.89–2.46) → weak, not
  robust association.
- Max VIF 4.6 (oncology). Figure `07_pre_post_2016_odds_ratios.png`; tables
  `table_pre_post_models.csv`, `table_pre_post_m3_coefficients.csv`. Wording: associations only.
- **D50** (for Blocks 15–17, requested at sign-off of Block 13): interpret the association
  "placebo-controlled OR 2.01" in domain terms (e.g. link to patient trials, trial size,
  complexity) – check confounding/interactions before interpreting.

## 2026-11-05 – Block 14: Sensitivity analyses (notebook 05, part 2)

- S1 without retrospectively registered trials (725 in A / 705 in B): adjusted OR (a) A 2.63,
  B 1.78. S2 start ≤ 2019 / ≤ 2020: 2.30 / 2.46. S5 2-year window: 1.70. S6 worst case
  (Unknown = terminated; 246 pre / 189 post): A 2.56, B 1.71 → period association robust.
- S3 subgroups (adjusted OR, 3-year window): healthy volunteers 2.14 (excl. oncology 2.05),
  patients 1.74 (excl. oncology 1.71); subgroup models use industry yes/no (quasi-separation of
  the 3-level sponsor variable among healthy-volunteer trials: 0/24 terminations in the
  government/network group) and merge 9 patient trials of the healthy-volunteer indication group
  into "Other diseases" (sparse cell) – no convergence warnings.
- **S4 interaction period × healthy volunteers**: A 0.62 (0.45–0.85, p = 0.003), excl. oncology
  0.80 (p = 0.28); 3-year window 1.36 (0.92–2.00, p = 0.13), excl. oncology 1.24 (p = 0.41) →
  no robust difference of the period effect; A result driven by right-censoring of long patient
  trials. Safety-related interaction (exploratory): 1.46 (0.61–3.48).
- (b) safety-related: ORs 1.44–1.60, CI includes 1 except in A and S1 A → no robust change.
- **S7 EudraCT (D21 vs. D22)**: prematurely ended 31.9 % (lenient) vs. 17.8 % (strict) of 1,855
  ended trials.
- Figure `08_sensitivity_analyses.png`; tables `table_sensitivity_overview.csv`,
  `table_sensitivity_subgroups.csv`, `table_sensitivity_interaction.csv`,
  `table_eudract_definition_sensitivity.csv`.

## 2026-11-05 – Block 15: Modelling setup (notebook 06, part A)

- **D51 – prediction target** (expert decision): terminated within 3 years after start; cohort =
  all trials started 2005–2020 (incl. 2016), any status except Withdrawn (7,874 trials, 543
  positives = 6.9 %). Analysis-set outcome only as sensitivity variant. Running/unknown and
  later terminations count as negative → the model predicts *early* termination.
- **D53 – evaluation**: main = repeated stratified 5-fold CV (3 repeats, seed 2026); robustness =
  temporal split train 2005–2015 (5.7 % positives) / test 2017–2020 (9.6 %), with and without
  start year.
- Leakage: feature list per Block 6; automatic single-feature AUC check – none > 0.75 (max 0.57).
- **D30 done**: redundant pairs blinded/masking_level 0.98, multinational/log_n_countries 0.98,
  site_outside_europe/site_in_us 0.92, log_n_locations/log_n_countries 0.85; design cluster
  placebo–blinded–randomized; VIF > 5 for these and large indication groups.
  **D52**: logistic regression uses a reduced set (without masking_level, log_n_countries,
  site_in_us, site_outside_europe); design-cluster coefficients interpreted jointly; random
  forest uses all features.
- **D50 done**: placebo association concentrated in healthy-volunteer trials (early termination
  9.2 % vs. 3.0 %; adjusted OR 3.35 vs. 1.61 in patients; interaction p = 0.002; not explained by
  number of sites). Interpretation: placebo marks randomised double-blind dose-escalation studies
  of new compounds (early-development attrition), vs. open-label crossover PK/BE/DDI studies.
- Baselines: random PR-AUC 0.069; rule of thumb (oncology + healthy volunteers + Phase 1/2)
  PR-AUC 0.079, ROC-AUC 0.55 (CV) – early termination is hard to predict from registry data.
- **D54 – README wording** (expert): the highest early-termination risk of FIH-like
  (placebo-controlled) healthy-volunteer trials holds **within healthy-volunteer trials**
  (9.2 % vs. 3.0 %), not overall – oncology trials are higher.

## 2026-11-05 – Block 16: Models (notebook 06, part B)

- **D55 – modelling procedure**: LR (reduced set, D52) and RF (all features), class_weight
  balanced; variants core / + start year / + start year + ⚠️ site. **Nested CV**: outer repeated
  stratified 5-fold × 3 (15 test folds), inner stratified 3-fold grid search (LR C ∈ {0.01, 0.1, 1};
  RF min_samples_leaf ∈ {10, 40, 120}, max_features ∈ {sqrt, 0.5}, 300 trees). OOF predictions
  averaged over repeats; bootstrap (1,000) CIs and paired comparison with the rule of thumb.
  Recalibration and the sensitivity variant use the most frequent tuned parameters of the best
  model (RF + site: max_features 0.5, min_samples_leaf 40) as fixed parameters (runtime).
- Results: PR-AUC OOF LR/RF core 0.102/0.099, + start year 0.109/0.106, + site 0.125/0.123
  (random 0.069, rule of thumb 0.078); ROC-AUC 0.63–0.67; top-10 % risk group 14.2–14.4 %
  terminated vs. 6.9 % average. LR ≈ RF.
- Calibration: balanced weights → mean predicted 43 % (Brier 0.206); recalibrated / unweighted LR
  Brier 0.063 vs. 0.064 for the prevalence → probabilities hardly informative.
- Temporal test (test prevalence 9.6 %): PR-AUC 0.13–0.17, ROC-AUC 0.59–0.66; start year adds
  nothing (coefficient ≈ 0 under strong regularisation).
- Sensitivity (analysis-set outcome): PR-AUC 0.39 vs. 0.25, ROC-AUC 0.76 (late terminations of long
  trials easier to recognise; censoring-affected).
- **Conclusion (wording for README/LinkedIn)**: registry data alone predict early termination only
  to a limited extent.

## 2026-11-07 – Decisions at sign-off of Block 16

- **D56 – main model for the README**: the model **without** ⚠️ site features
  ("core + start year"), because site/country information may have been updated after the
  start; the model with ⚠️ features is reported only as an **upper bound**.
- **D57 – interpretation**: LR and RF perform alike → Block 17 interprets primarily the
  **logistic regression** (core + start year, recalibrated).
- Temporal test results to be stated explicitly in README (2005–2015 → 2017–2020, test
  prevalence 9.6 %): LR core + start year PR-AUC 0.126 (0.105–0.159), ROC-AUC 0.59, top-10 %
  13.0 %; RF core + start year 0.133 (0.111–0.162), ROC-AUC 0.62, top-10 % 14.3 %; upper bound
  RF + site 0.169 (0.138–0.212), ROC-AUC 0.66; rule of thumb 0.098, random 0.096.

## 2026-11-07 – Block 17: Interpretation of the main model (notebook 06, part C)

- Main model (D56/D57): LR core + start year, C = 0.01, balanced, recalibrated (sigmoid inside the
  training folds): PR-AUC 0.110, ROC-AUC 0.64, Brier 0.063, mean predicted = observed 6.9 %.
- **Top-10 % scenario** (per 1,000 trials): 100 flagged – 12 true (precision 11.5 %), 89 false;
  recall 17 % (57 early terminations missed). 5/20/30 % flagged: recall 9/34/48 %, precision
  ~11–12 %. Upper bound RF + site: precision 14.5 %, recall 21 %.
- **Grouped permutation importance** (15 test folds × 5 shuffles, PR-AUC drop): design cluster
  0.019 ± 0.016, start year 0.013 ± 0.012, sponsor 0.012 ± 0.006; other groups ≈ 0.
- **Odds ratios** (unpenalised LR): design cluster joint Wald p < 0.001, RDBPC vs. open OR 2.02
  (1.51–2.70); industry 1.91; start year 1.05/year; crossover lowest; "not reported" categories =
  data-quality proxies; indication/healthy volunteers not independently associated with *early*
  termination.
- **D50 completed**: placebo OR 3.83 (healthy volunteers) vs. 1.30 (patients); subgroup models use
  industry yes/no, drop includes_children in healthy-volunteer trials (0/49 events) and merge
  factorial into parallel in patient trials (0/21 events) – converged without warnings.
- Figures `10_top10_confusion_matrix.png`, `11_feature_importance.png`; tables
  `table_permutation_importance_*.csv`, `table_main_model_odds_ratios.csv`. Wording: associations.

## 2026-11-09 – Block 18: EudraCT / EU CTR description (notebook 07, part A)

- New notebook `07_registry_transparency.ipynb` (Part A = B18; Parts B/C follow in B19/B20).
- **Study mix of the EU CTR Phase I download (2,823 trials):** Phase I/II 2,144 (75.9 %), Phase I
  only 565 (20.0 %), Phase I + III/IV 114; children or PIP 948 (33.6 %). Adults without PIP and
  Phase I only: **4 (0.1 %)**, none with the first-in-human flag.
- **D21 vs. D22 (side by side, ended trials n = 1,855):** 31.9 % (29.8–34.0) vs. 17.8 % (16.1–19.6).
  Single country (n = 1,090) 23.7 % under both; multi-country (n = 765) 43.5 % vs. 9.4 %. Adults
  no PIP 32.2 vs. 18.5 %; children/PIP 31.1 vs. 16.0 %; Phase I only (ended = all children/PIP)
  25.9 vs. 16.9 %; Phase I/II 33.4 vs. 18.2 %. Table `table_eudract_D21_vs_D22.csv`.
- **No termination reason:** section P of all 142 raw pages contains only "End of Trial Status"
  and "Date of the global end of the trial" (checked programmatically) → RQ1b not answerable for
  EudraCT.
- **Visibility gap (D58 – method):** ClinicalTrials.gov Phase 1/1/2 trials with a target-country
  site and a classic EudraCT number (`YYYY-[0-4]NNNNN-CC`; CTIS numbers excluded), matched to the
  EU CTR Phase I download:
  - adult Phase 1: 131 / 3,319 found (3.9 %); all 131 are classified in EudraCT as Phase I/II (103),
    Phase I + III/IV (7) or PIP/paediatric (21) – none as adult Phase-I-only;
  - Phase 1 incl. children 83.6 %, Phase 1/2 adults 59.6 %, Phase 1/2 incl. children 80.0 %;
  - spot check: 40 random missing adult Phase 1 trials searched in the full EU CTR (all phases):
    **0/40 found** (3/3 positive controls found);
  - CTIS: 376 of 399 transitioned adult non-PIP Phase I trials (94 %) were not in the EU CTR
    Phase I download (all transitioned: 528 / 952).
- **Results availability (D59):** EU CTR filter "trials with results" downloaded (1,659 trials on
  2026-11-09 vs. 1,658 on 2026-10-27): 58.8 % of all; Completed 76.4 %, Prematurely Ended 69.4 %,
  Ongoing 17.6 %, Transitioned 1.5 %.
- **Study-mix caveat (D60):** EU CTR ended trials vs. ClinicalTrials.gov analysis set: Phase I/II
  78.7 vs. 21.8 %, children 27.5 vs. 5.9 %, healthy volunteers 11.6 vs. 46.7 %. EudraCT termination
  shares are never shown next to ClinicalTrials.gov shares without this caveat; a stratum-wise
  comparison follows in Block 20.
- Figures `12_eudract_visibility_gap.png`, `13_eudract_definitions.png`; tables
  `table_eudract_study_mix.csv`, `table_eudract_D21_vs_D22.csv`, `table_eudract_visibility_gap.csv`,
  `table_eudract_visibility_spotcheck.csv`, `table_eudract_results_availability.csv`,
  `table_eudract_vs_ctgov_study_mix.csv`.

## 2026-11-09 – Additions to Block 18 (requested at sign-off)

- **Legal basis of the visibility gap (D61):** Commission guideline 2008/C 168/02 (OJ C 168,
  3.7.2008, p. 3), Section 3: "phase I trials […] are excluded from publication"; public
  information covers Phase II–IV. Paediatric trials (incl. Phase I) public under Art. 41 Regulation
  (EC) No 1901/2006 / guideline 2009/C 28/01. Results: guideline 2012/C 302/03, Section 5 – "only
  result-related information on non-paediatric Phase-I clinical trials is not made public".
  Added to notebook 07 (A1), footer of figure 12 and `docs/regulatory_background.md`. Figure 12 now
  also shows the spot check (0 of 40 found anywhere in the EU CTR).
- **Results obligation (D62):** guideline 2012/C 302/03, Section 4.3: 12 months after end of trial
  (6 months paediatric; premature end = end of trial); mandatory since 21 July 2014; retrospective
  posting for earlier trials (Section 4.6.1). Results where posting was due (ended, global end
  ≥ 12 months before download; n = 1,513): **80.0 % (78.0–82.0)**; Completed 81.3 %, Prematurely
  Ended 77.0 %; ended before 21 Jul 2014 76.5 %, from 21 Jul 2014 81.4 %. 342 ended trials without a
  global end date excluded. Measures availability at the download date, not timeliness.

## 2026-11-09 – Block 19: CTIS and cross-registry matching (notebook 07, part B)

- **CTIS publication rules (D63):** documented with sources (EMA/263067/2023 revised rules, applicable
  from 18 June 2024; ACT EU quick guide on historical trials; Art. 81 CTR). Category 1 adult:
  reduced structured data at decision, rest + protocol + results 30 months after end of trial; early
  termination notifications published immediately; historical trials: structured data only.
- CTIS Phase I: 3,522 trials (Phase I 2,354, I/II 1,168; ended 1,603; transitioned 952).
- Early termination among ended: 27.5 % lenient vs. 22.5 % strict; transitioned 42.8 vs. new 22.0 %;
  Phase I 21.6 vs. Phase I/II 51.6 %.
- **D25 with right-censoring:** ended 73 % (HV) vs. 31 % (patients); early termination among ended
  8.3 vs. 51.2 %, among all trials 6.2 vs. 19.9 %; cohort new CTR decision 2022–2023: 7.0 vs. 34.2 %
  among all (ended 91 vs. 47 %). Figure 14 shows both denominators side by side.
- **Coded reason (D64):** 1,049 member-state notifications in 536 trials (Sponsor Decision 82.0 %).
  Trial level (ended + early terminated, n = 441): Sponsor Decision in ≥ 1 MS 80.5 %, only code 79.4 %.
  Correction: the earlier "97 %" was 429/441 – 429 refers to all 536 trials with early termination
  (80.0 %), i.e. two denominators were mixed. ClinicalTrials.gov no specific reason 20.9 %
  (8.5 % + 12.4 %). Harmonised comparison in `table_reasons_ctis_vs_ctgov.csv`, figure 15.
- Same trials (CTIS early terminated + ClinicalTrials.gov Terminated, n = 165): of 133 with only
  "Sponsor Decision" in CTIS, ClinicalTrials.gov gives Strategic/Business 68, Efficacy 9, Safety 7,
  Recruitment 4, Funding 2, Other 11, unspecified 26, not stated 6 (rules v2 via new module
  `notebooks/why_stopped_rules.py`, verified 1,154/1,154 identical to stored v2 labels).
- **ID linkage:** 1,844 / 3,522 (52.4 %) CTIS trials linked to an NCT number (CTIS field 1,105 valid,
  2 placeholders "NCT00000000"; CTIS only 544, CT.gov only 739, both 561; 9 trials with > 1 NCT).
  HV 23.7 % vs. patients 67.3 %; Phase I 44.0 vs. I/II 69.3 %; industry 55.1 vs. 41.6 %;
  transitioned 75.4 vs. new 43.8 %. 1,829 of 1,832 NCT numbers found via API (2026-11-09).
- Status agreement: CTIS ended early → ClinicalTrials.gov Terminated 165/292 (56.5 %), Completed 58,
  still active 58.
- New raw data `data/raw/ctgov_ctis_links/` (19 API batches). Figures 14, 15; tables
  `table_ctis_early_termination`, `table_ctis_hv_vs_patients_censoring`, `table_reasons_ctis_vs_ctgov`,
  `table_reasons_same_trials`, `table_ctis_nct_linkage`, `table_ctis_ctgov_status_agreement`.

## 2026-11-09 – Sign-off of Block 19: correction "97 %" → 80 % applied everywhere

- Confirmed by the project owner. Search over the whole project (docs, builders, all notebooks incl.
  outputs, README, linkedin drafts, tables): the wrong figure stood only in notebook 01 (Part C
  interpretation; markdown cell edited in place without re-running the download) and its builder.
  Log entry Block 4 now states the denominator (429 of 536 = 80.0 %). README / LinkedIn drafts:
  no occurrence. The only remaining mention of "97 %" is the correction note under D64.
- Additions at sign-off of Block 19:
  - Figure 15 now has a second panel: same trials, 133 with only "Sponsor Decision" in CTIS → 101
    (76 %) with a specific reason on ClinicalTrials.gov ("classified by rules v2, not expert-reviewed").
  - Status agreement under the strict definition (D65): CTIS early termination in ALL member states
    (n = 224) → ClinicalTrials.gov Terminated 139 (62.1 %), Completed 35, Active 40; mixed EU status
    (n = 68) → 26 (38.2 %). Definition explains part of the gap, not all of it (global vs. EU status,
    update delays: 21 of 75 non-terminated records not updated for > 12 months).
    Table `table_ctis_ctgov_status_agreement_strict.csv`.
  - Limitation added: only 24 % of CTIS healthy-volunteer trials have an NCT link → ClinicalTrials.gov
    covers European healthy-volunteer trials only partially.

## 2026-11-09 – Block 20: Comparison of the three registries (notebook 07, part C)

- **D66 – common strata** from each registry's own fields: S1 Phase I only · adults · healthy volunteers;
  S2 Phase I only · adults · patients only; S3 Phase I/II · adults · patients only; S4 Phase I only ·
  incl. children; S5 Phase I/II · incl. children. EU CTR Phase I + III/IV excluded; groups with n < 20
  not shown. Denominator: ended trials in each registry.
- Results (lenient; strict in brackets):

  | Stratum | ClinicalTrials.gov | EU CTR | CTIS (right-censored) |
  |---|---|---|---|
  | All ended | 14.5 % (n = 7,960) | 32.1 % (17.9 %), n = 1,780 | 27.5 % (22.5 %), n = 1,603 |
  | S1 HV, adults, Phase I | 6.3 % (n = 3,498) | 4.2 % (n = 24, all PIP) | 8.1 % (7.9 %), n = 865 |
  | S2 patients, adults, Phase I | 19.0 % (n = 2,497) | n = 2 | 49.7 % (41.7 %), n = 396 |
  | S3 patients, adults, Phase I/II | 26.0 % (n = 1,321) | 34.9 % (20.0 %), n = 1,134 | 55.1 % (39.7 %), n = 267 |
  | S4 children, Phase I | 14.6 % (n = 226) | 27.9 % (18.0 %), n = 294 | 41.7 % (33.3 %), n = 24 |
  | S5 children, Phase I/II | 26.5 % (n = 245) | 40.1 % (15.3 %), n = 202 | 41.7 % (30.6 %), n = 36 |

- **D67 – same-trial check EudraCT ↔ ClinicalTrials.gov** (n = 542, ended in both, linked by EudraCT
  number): ClinicalTrials.gov Terminated 30.6 %, EU CTR D21 32.8 %, D22 12.7 %; agreement D21 76.8 %
  (kappa 0.46), D22 74.0 % (kappa 0.27). → The overall difference (14.5 vs. 32.1 %) is mainly study
  mix; ClinicalTrials.gov "Terminated" corresponds more closely to the lenient EudraCT definition.
- **Transparency matrix** (figure 17, `table_registry_transparency.csv`): visibility of adult Phase I,
  status, reason, results, machine-readable access, cross-registry IDs, period. New counts: EU CTR
  protocols with NCT number (field A.5.2) 629 / 2,823 (22 %); ClinicalTrials.gov trials with a
  EudraCT/EU CT number 48 %; results posted ClinicalTrials.gov 23 % (terminated 33 %), CTIS 20 % of
  ended trials.
- Figures `16_registry_comparison_strata.png`, `17_registry_transparency_matrix.png`; tables
  `table_registry_comparison_strata.csv`, `table_same_trials_eudract_ctgov.csv`,
  `table_registry_transparency.csv`.


## 2026-11-09 – Sign-off of Block 20: figure changes

- Figure 17: EU CTR "Results publicly available" → not available (red): adult non-PIP Phase I results
  are never published (2012/C 302/03, Section 5); the 80 % where due concern other trials – consistent
  with row 1. Row "Period covered" now neutral grey ("context, not rated"). ClinicalTrials.gov
  "Termination status" text: "not always updated (469 'Unknown', start 2005–2022)" (rating unchanged).
- Figure 15: categories labelled in the right panel; "Strategic/business/funding" = 68 strategic/business
  + 2 funding = 70 (explains 68 in the text vs. 70 in the figure).
- Figure 16: subtitle "Most comparable group (adult healthy-volunteer Phase I): similar in all registries".

## 2026-11-10 – Block 21: LinkedIn figures (draft for review)

- Selection agreed with the project owner (6 figures, this order): 1 key numbers · 2 termination
  reasons · 3 healthy volunteers (stratum S1) · 4 visibility gap · 5 same trials ("Sponsor decision") ·
  6 transparency matrix. Flow diagram only in the README.
- Style (D68): 1080 × 1350 px (4:5), title = key message (19 pt bold), body text ≥ 12 pt, large
  numbers 16–30 pt, category labels above the bars (no axes), source + access date on every figure
  (8 pt). Colours: shared project palette; safety highlighted, other categories grey.
- All numbers read from `data/processed` tables (script `_working_files/linkedin/build_linkedin.py`,
  output `linkedin/01…06_*.png`).
- Figure 2: 9 categories → 6 (COVID-19 and funding under "Other"; "Sponsor decision (unspecified)" +
  "Not stated" = "No specific reason given", as in figure 15).
- Figure 3 title: **"4–8 %"** instead of the suggested "6–8 %": EU CTR S1 = 4.2 % (n = 24, all PIP trials,
  95 % CI 0.7–20.2); ClinicalTrials.gov 6.3 %, CTIS 8.1 %.

## 2026-11-11 – Block 21 closed: LinkedIn figures final

- Figures 1, 2, 4, 6 approved. Changes at sign-off:
  - Figure 3: EU CTR bar removed (n = 24, PIP trials only, 95 % CI 0.7–20.2 % – not robust); line
    "EU CTR: too few visible trials (n = 24)". Title "Healthy-volunteer Phase I trials rarely stop
    early: 6–8 %" (ClinicalTrials.gov 6.3 %, CTIS 8.1 %).
  - Figure 5: neutral title "CTIS says 'Sponsor decision' – ClinicalTrials.gov says why" (the
    finding concerns the coding system, not sponsor intent).
  - All six: page number "1/6" … "6/6" and author line "Wroud Mrae, Pharmacist".
- Terms of use (docs/data_sources_and_terms.md): EMA must be acknowledged for CTIS content → all CTIS
  source lines (notebook 07 figures 14–17 and LinkedIn figures) now name the European Medicines Agency.

## 2026-11-11 – Block 22: README (draft for review)

- README rewritten (English): key findings table, background (TGN1412, BIA 10-2474, FIH guideline
  2007/2017), RQ1–5, data sources with access dates and attribution, short methods, results per RQ
  with 9 figures (flow diagram only here), limitations summary, repository structure, notebook table,
  reproducibility, disclaimer, licence.
- Wordings applied as decided: D47 ("test-retest reliability of a single expert rater"), D54 (FIH-like
  risk highest *within* healthy-volunteer trials, not overall), D56 (main model without site
  features; site model as upper bound only), temporal test results (D57 sign-off), Efficacy/Futility
  uncertainty (10.1 % final vs. 15.3 % weighted expert estimate), D25 (CTIS HV vs. patients only with
  right-censoring), associations only.

## 2026-11-11 – Block 22 closed: README final

- LICENSE: "Copyright (c) 2026 Wroud Mrae".
- References section (8 entries) with citations [1]–[8] in Background and RQ5; checked against
  PubMed (PMID 16908486: N Engl J Med 2006;355(10):1018–28; PMID 27806235: N Engl J Med
  2016;375(18):1717–25), the EMA guideline page (EMEA/CHMP/SWP/28367/07 effective 1 Sep 2007;
  Rev. 1 effective 1 Feb 2018; note: Rev. 1 title adds "and early clinical trials"), EUR-Lex and the
  EMA PDF of the revised CTIS rules. BIA 10-2474 wording corrected to the published account
  ("one volunteer became brain dead, others developed an acute neurological disorder, partly with
  lasting deficits").
- Key finding 7 reworded: 3,319 adult-only Phase 1 trials with a EudraCT number → 131 (3.9 %) in the
  public register, none as adult Phase I (numbers from notebook 07, A5).
- Prediction table: nested-CV PR-AUC with bootstrap CI from `table_model_performance_cv.csv`
  (main model 0.109, 0.096–0.127); recalibrated 0.110 explained in a footnote.
- **D69 – industry OR explanation (checked with the data):** RQ2 counts termination at any time,
  the model termination within 3 years; academic trials are terminated later (median 3.3 vs. 2.4
  years; 45 % vs. 59 % within 3 years) → crude early-termination 7.6 % vs. 4.7 % (OR 1.64); industry
  runs more healthy-volunteer trials (48 % vs. 28 %) → OR 1.79 after adjusting for healthy volunteers
  alone, 1.91 in the full model.
- New section "How this project was made" (Claude Code support for the code; questions, design,
  decisions, blinded expert review and interpretation by the author).
- Licence (owner decision, 11 Nov 2026): code MIT; figures and texts (README, figures, LinkedIn
  graphics) CC BY 4.0, © 2026 Wroud Mrae (full text in LICENSE-CC-BY-4.0.txt, official legal code
  retrieved 11 Nov 2026); registry data remain under the registries' terms.

## 2026-11-11 – Block 23a: full offline re-run of notebooks 01–07

- **D70 – offline mode:** new module `notebooks/offline_guard.py`; with the environment variable
  `PHASE1_OFFLINE=1` every network connection raises an error. Notebook 01 then takes the EU CTR
  search counts from `euctr_phase1_metadata.json` (the only live calls that were not cached);
  notebook 07 uses only cached files. Without the variable the notebooks behave as before.
- Re-run 11 Nov 2026, 18:34–18:53 (script `_working_files/run_all_offline.sh`): all 7 notebooks
  rebuilt from the builders and executed in order – 0 errors, 0 cells not executed, no warnings;
  the LinkedIn figures were regenerated afterwards.
- Comparison with a snapshot taken before the re-run (`_working_files/check_rerun.py`):
  - 54 data files (processed + interim): identical except `model_cv_folds.csv`, where the Brier
    score differs in 9 of 120 fold rows by at most 5.6e-17 (last digit of floating-point output) –
    numerically identical, no effect on any reported number;
  - all figures in `figures/` and all 6 LinkedIn images: pixel-identical;
  - 24 README numbers recomputed from the new outputs: all found unchanged in the README; temporal
    test table identical to the README.
- No corrections were needed.

## 2026-11-11 – Block 23b/c: LinkedIn post draft, backup

- Draft `linkedin/post_draft.md` (English, 1,215 characters incl. hashtags): reference to the author's
  GCP presentation on TGN1412 and BIA 10-2474, five findings with numbers from the README, explicit
  "associations, not causal effects", "registered trials only", link placeholder (publication
  decided in Phase 7). Draft only – to be checked by the author before publication.

## 2026-11-11 – Block 24 (buffer): final corrections and Phase 7 preparation

- README: decision range D01–D70; offline re-run instructions (PHASE1_OFFLINE=1, D70); line break in the
  top-10 % sentence; snapshot / modification statement in "Data sources" (ClinicalTrials.gov terms).
- Numbers confirmed (no change):
  - safety-related, 3-year window: OR 1.48 (0.89–2.46) = standard logistic regression; 0.90–2.44 is the
    Firth-penalised model of the same analysis (both in `table_pre_post_models.csv`, row "B 3-year
    window, (b)"); the README reports the logistic model, as for all other ORs.
  - Efficacy/Futility: 9.4 % = rule version v1 on all 1,154 texts (Block 8/9); 9.6 % = rules v2;
    **10.1 %** (116/1,154) = final labels (expert where reviewed, otherwise v2) – the expert review
    added 9 and removed 4 Efficacy/Futility labels compared with v2.
- LinkedIn post draft: points 3 and 4 and the Claude Code sentence as requested; shortened elsewhere to
  stay below 1,300 characters (1,293 incl. hashtags).
- Phase 7 preparation: ClinicalTrials.gov Terms and Conditions checked and recorded; publication rules
  for code / aggregate tables / trial-level data / raw data in `docs/data_sources_and_terms.md`;
  file list public (109 files, 10.7 MB) vs. private (323 files, 209 MB) and link options in
  `docs/publication_plan.md`. Nothing published.

## 2026-11-12 – Phase 7 preparation: publication package (owner decisions)

- Owner decisions: link = public GitHub repository (browser upload by the owner); notebooks published
  with outputs; expert labels published now without registry texts; no second rater planned.
- `validation/expert_labels_public.csv` (302 rows: main review 218, hold-out 34, retest 50): review_id,
  nct_id, sample, stratum, weight, expert primary reason (final, after documented corrections),
  safety yes/no, rules-v1 label, documented correction IDs. No free text. None of the existing files
  contained this combination (validation_results_v1: main review only, blinded labels, plus free text).
- Published validation files cleaned: validation_results_v1 without `text`, `matched_keywords`,
  `negated_mentions`; holdout_results without `text`; expert_corrections K7 quote replaced;
  retest_results unchanged. Originals stay in the project (used by notebook 03).
- Notebook outputs scanned: no e-mail addresses, phone numbers or contact names (the "phone" hits were
  EudraCT/CTIS numbers); one user path (notebook 01 "Project directory") → now folder name only;
  notebook 01 re-run offline, all 7 interim files identical. One user path in this log replaced.
- data/raw/README.md published (instructions only); row `ctgov_csv_check` corrected (not performed).
- README: link to the expert labels; note on what the public version contains and what re-running needs.
- Package `phase1-terminations-europe_PUBLIC.zip` built with `build_public_package.py`; checks: no
  file > 25 MB, all relative links resolve, no e-mail addresses, no user paths, .gitkeep only in
  otherwise empty folders.

## 2026-11-12 – Fix of the public expert labels (found by the project owner)

- **Error:** in `expert_labels_public.csv` the retest rows took the primary reason from the column
  `expert_retest` of `why_stopped_retest_results.csv`. That column was **not** the re-rating: it was the
  first-round main-review label copied from the sample key during a merge (identical to `expert_first`
  in 50/50 rows), while safety came from the original re-rating → contradiction (e.g. review 22:
  "Safety" with safety "no") and 49/50 apparent agreement instead of the reported 42/50.
  The reported reliability figures were never affected (notebook 03 computed them from the correct
  column `expert_primary`).
- **Fix (notebook 03):** retest output with unambiguous names: `retest_id` (was `rater2_id`),
  `retest_primary_original`, `retest_safety_original`, `retest_other_original`,
  `retest_comment_original`, `first_round_primary`, `first_round_safety`, plus
  `retest_primary_corrected_doc` / `retest_safety_corrected_doc` (documentation only, 9 primary labels
  differ); misleading duplicate column dropped; assertion that the file reproduces the reported kappa.
  Notebook 03 re-run offline: 0 errors; all files in `data/processed` and all figures identical; only
  `why_stopped_retest_results.csv` changed. Reported values unchanged: weighted agreement 83.9 %,
  weighted kappa 0.80; test-retest 84.0 % (42/50), kappa 0.78 (0.65–0.91), safety kappa 0.96.
- **Labels file rebuilt** (script `build_expert_labels.py`): retest rows = original re-rating (reason and
  safety); new columns `expert_primary_first_round`, `expert_safety_first_round` (main review and
  hold-out); check that no row has primary reason Safety with safety "no".
- **Recomputed from the published files only:** expert_labels_public → test-retest 84.0 % (42/50),
  kappa 0.78, safety kappa 0.96; validation weighted agreement 83.9 %, weighted kappa 0.80; identical
  from the cleaned `why_stopped_retest_results.csv` and `why_stopped_validation_results_v1.csv`.
- `docs/data_dictionary.md`: new section on all files in `validation/` (meaning of every column,
  published / private).
