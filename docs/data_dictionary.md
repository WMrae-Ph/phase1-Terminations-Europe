# Data dictionary

Analysis dataset: `data/processed/ctgov_analysis_dataset.parquet` (one row per trial). Filled in
during Blocks 5–7.

| Variable | Type | Source field | Description |
|---|---|---|---|
| nct_id | text | identificationModule.nctId | ClinicalTrials.gov identifier |
| overall_status | category | statusModule.overallStatus | COMPLETED or TERMINATED in the analysis set |
| terminated | 0/1 | derived | **Outcome**: 1 = TERMINATED, 0 = COMPLETED |
| why_stopped | text | statusModule.whyStopped | Free-text reason for termination (classified in notebook 03) |
| start_date_dt | date | statusModule.startDateStruct.date | Start date (month-only dates set to day 1) |
| start_year | integer | derived | Year of start_date_dt (2005–2022) |
| period | category | derived | pre (2005–2015), transition (2016), post (2017–2022) |
| industry_sponsor | 0/1 | sponsorCollaboratorsModule.leadSponsor.class | Lead sponsor class INDUSTRY ✅ |
| sponsor_group | category | leadSponsor.class | Industry / Academic & other (OTHER) / Government, network & other ✅ |
| industry_collaborator | 0/1 | collaborators[].class | Any industry collaborator ✅ |
| healthy_volunteers | 0/1 | eligibilityModule.healthyVolunteers | Accepts healthy volunteers; 6 missing imputed from condition text ✅ |
| healthy_volunteers_imputed | 0/1 | derived | Flag for imputed value |
| includes_children | 0/1 | eligibilityModule.stdAges | Age group includes CHILD ✅ |
| male_only | 0/1 | eligibilityModule.sex | Sex = MALE ✅ |
| phase_1_2 | 0/1 | designModule.phases | Phase 1/2 (vs. Phase 1) ✅ |
| randomized | 0/1 | designInfo.allocation | RANDOMIZED ✅ |
| masking_level | 0–4 | designInfo.maskingInfo.masking | NONE 0, SINGLE 1, DOUBLE 2, TRIPLE 3, QUADRUPLE 4 (missing → 0) ✅ |
| blinded | 0/1 | derived | masking_level > 0 ✅ |
| placebo | 0/1 | armGroups[].type, interventions[].name, armGroups[].label | PLACEBO_COMPARATOR arm or "placebo" in a name ✅ |
| intervention_model | category | designInfo.interventionModel | SINGLE_GROUP, PARALLEL, CROSSOVER, SEQUENTIAL, FACTORIAL, NOT_REPORTED ✅ |
| primary_purpose_group | category | designInfo.primaryPurpose | TREATMENT, BASIC_SCIENCE, PREVENTION, OTHER (incl. rare), NOT_REPORTED ✅ |
| has_dmc_cat | category | oversightModule.oversightHasDmc | yes / no / not reported ✅ |
| biological, drug | 0/1 | interventions[].type | BIOLOGICAL or GENETIC; DRUG ✅ |
| n_locations, log_n_locations | int / float | contactsLocationsModule.locations | Number of listed sites (log1p) ⚠️ |
| n_countries, log_n_countries, multinational | int / float / 0/1 | locations[].country | Number of site countries ⚠️ |
| site_outside_europe, site_in_us | 0/1 | locations[].country | Any site outside Europe / in the US ⚠️ |
| registered_after_completion | 0/1 | studyFirstSubmitDate vs. primaryCompletionDate | Registered after primary completion ❌ (descriptive / sensitivity) |
| registered_prospectively | 0/1 | studyFirstSubmitDate vs. startDate | Registered ≤ 30 days after start ❌ |
| enrollment_actual | int | enrollmentInfo (type ACTUAL) | Actual enrollment ❌ |
| has_results_posted | 0/1 | hasResults | Results posted on ClinicalTrials.gov ❌ |
| indication_group | category | conditionBrowseModule (MeSH terms + ancestors), conditions | 9 groups, see `mappings/condition_groups.csv` and overrides ✅ |
| indication_source | category | derived | mesh / free_text / healthy_volunteer_rule / override / unclassified_fallback |
| override_case | text | derived | Borderline case ID if an override was applied (B2, B3, B6, B8, B10, FT) |
| n_disease_groups_matched | int | derived | Number of disease groups matched before priority resolution |

Legend: ✅ known at start (model) · ⚠️ may be updated after start (model + sensitivity without) ·
❌ post-start information (descriptive only).

## Termination reasons (`data/processed/why_stopped_classified.parquet`, terminated trials only)

| Variable | Type | Description |
|---|---|---|
| reason_Safety … reason_Not stated | 0/1 | Multi-label flags per category (9 labels incl. COVID-19 and Sponsor decision (unspecified)) |
| reason_categories | text | All assigned categories, `|`-separated |
| n_reasons | int | Number of assigned categories |
| primary_reason | category | Single main reason by priority (D34) |
| reason_flags | text | Sub-flags, e.g. covid, supply, benefit_risk, interim_analysis, stopping_criteria, unmatched |
| matched_keywords | text | Audit trail: category and matched text for every hit |
| negated_mentions | text | Keywords that were found but ignored because negated |

## Final termination reasons (`data/processed/why_stopped_final.parquet`) – input for notebooks 04–06

| Variable | Type | Description |
|---|---|---|
| primary_reason_final | category | Expert label where reviewed (252 trials), otherwise algorithm v2 (D41) |
| safety_related_final | 0/1 | Any safety aspect as a reason – expert (reviewed) or algorithm v2 |
| reason_source | category | expert (main review) / expert (hold-out) / algorithm v2 |
| primary_reason_v2, reason_categories_v2, reason_Safety_v2 | | Algorithm v2 output for all trials (audit) |

## Validation files (`validation/`)

Category labels everywhere: Safety · Efficacy/Futility · COVID-19 · Recruitment · Funding ·
Strategic/Business · Sponsor decision (unspecified) · Other · Not stated. Safety columns: yes/no (or
1/0). **Published** = in the public package (some only in a cleaned version, see
`docs/publication_plan.md`); **private** = contains registry free texts or blinding keys.

**Samples.** *Main review*: 218 texts, stratified: `S` = algorithm (v1) labelled Safety (all
included), `A` = borderline texts not labelled Safety but flagged for benefit-risk, interim analysis, stopping criteria or DMC recommendation (all included), `R` =
random sample of the remaining texts (60 of them, weight 14.4). *Hold-out*: 34 texts not in the main
review (28 COVID-19 texts + 6 texts whose label changed from rules v1 to v2). *Retest*: 50 of the 218
main-review texts re-rated by the same expert a few days later (no second rater exists).
"First round" = the expert's blinded rating as first submitted, before the documented corrections
K1–K10; "final" = after these corrections.

### `expert_labels_public.csv` (published) – one row per rating, no free text

| Column | Meaning |
|---|---|
| review_id | ID in the review workbook (main review and retest: main-review ID; hold-out: hold-out ID – the two numberings overlap, use together with `sample`) |
| nct_id | ClinicalTrials.gov identifier |
| sample | `main review` · `hold-out` · `retest` |
| stratum | main review / retest: `S`, `A`, `R` (see above); hold-out: selection reason (`COVID-19 (v2)`, `changed v1→v2`) |
| weight | inverse inclusion probability (main review only; 1 for S and A, 14.4 for R) |
| expert_primary_reason | main review / hold-out: **final** expert label (after corrections; used in the analysis); retest: the **original** re-rating (basis of the test-retest figures) |
| expert_safety_related | safety-related yes/no, same version as `expert_primary_reason` |
| expert_primary_first_round | main review / hold-out: blinded first-round label (basis of the validation metrics); empty for retest |
| expert_safety_first_round | safety yes/no of the first round; empty for retest |
| rules_v1_primary_reason | label of the rule-based classifier v1 (official accuracy) |
| documented_correction | IDs of the documented corrections (K1–K10) that concern this row; empty if none |

Recompute: validation = `expert_primary_first_round` vs. `rules_v1_primary_reason` with `weight`
(main review rows); test-retest = retest rows vs. main-review rows with the same `review_id`
(`expert_primary_first_round`, `expert_safety_first_round`).

### `why_stopped_validation_results_v1.csv` (published without `text`, `matched_keywords`, `negated_mentions`)

| Column | Meaning |
|---|---|
| review_id, nct_id, stratum, weight | as above |
| inclusion_prob | sampling probability (1 for S/A, 1/14.4 for R) |
| primary_reason, reason_categories, reason_Safety, reason_flags | rules v1 output (primary reason, all categories, safety flag 1/0, sub-flags) |
| matched_keywords, negated_mentions | *private*: rules-v1 audit trail quoting words from the registry text |
| expert_primary, expert_safety_related, expert_other, expert_comment | expert first round: primary reason, safety yes/no, further categories, comment (only "ambiguous") |
| text | *private*: registry free text (`why_stopped`) |
| algo, expert | copies of `primary_reason` (v1) and `expert_primary` used for the metrics |
| ambiguous | expert marked the text as ambiguous (True/False) |
| expert_safety, algo_safety | safety yes/no as 1/0 (expert, rules v1) |
| error_type | project's own description of the disagreement type |

### `why_stopped_holdout_results.csv` (published without `text`)

| Column | Meaning |
|---|---|
| review_id, nct_id | hold-out ID and identifier |
| selection | why the text is in the hold-out (`COVID-19 (v2)`, `changed v1→v2`) |
| primary_reason_v1, primary_reason_v2, reason_Safety_v1, reason_Safety_v2 | rules v1 and v2 output |
| expert_primary, expert_safety_related, expert_other, expert_comment | expert rating as given (before corrections K2–K6) |
| text | *private*: registry free text |

### `why_stopped_retest_results.csv` (published)

| Column | Meaning |
|---|---|
| retest_id | position in the shuffled retest workbook (1–50) |
| review_id, nct_id | main-review ID and identifier of the same text |
| retest_primary_original, retest_safety_original, retest_other_original, retest_comment_original | **original** re-rating (before any correction) – used for test-retest reliability |
| first_round_primary, first_round_safety | the expert's blinded first-round main-review rating of the same text |
| retest_primary_corrected_doc, retest_safety_corrected_doc | later corrected re-rating – documentation only, **not** used for reliability (9 primary labels differ) |

### `why_stopped_expert_corrections.csv` (published; quote in K7 replaced)

| Column | Meaning |
|---|---|
| correction_id | K1–K10 |
| review_round | `main review` or `hold-out` |
| review_id | ID within that round |
| field | corrected field (primary reason, safety, comment) |
| old_value, new_value | value before / after the correction |
| reason | reason, with the decision ID (e.g. D39, D42) |
| source | where the correction came from (expert answer to a query, corrected review file) |
| decision_date | date of the decision |

### Other files

| File | Status | Columns / content |
|---|---|---|
| `why_stopped_metrics_v1.csv` | published | per category: `n_algo (sample)`, `n_expert (sample)`, weighted `precision_w`, `recall_w`, `f1_w` (rules v1 vs. expert first round) |
| `condition_groups_borderline_review.csv` | published | borderline indication groupings: `case_id`, `question`, `current_assignment`, `alternative`, `n_trials`, `n_terminated`, `example_conditions` (condition terms from the registry), `decision`, `decided_by`, `decision_date`, `comment` |
| `condition_groups_decisions.csv` | published | `case_id`, `decision`, `decided_by`, `decision_date`, `comment` |
| `why_stopped_review_blinded.xlsx`, `why_stopped_holdout_blinded.xlsx`, `why_stopped_second_rater_blinded.xlsx`, `templates/why_stopped_second_rater_TEMPLATE_blank.xlsx` | private | blinded workbooks: sheet *Review* with `review_id`, `nct_id`, `why_stopped (original text)`, `expert_primary_category`, `expert_safety_related (yes/no)`, `expert_other_categories (optional)`, `comment (optional)`; sheet *Instructions* (short codes S/E/C/R/F/B/D/O/N) |
| `why_stopped_review_expert_filled.csv`, `…_corrected.csv`, `why_stopped_holdout_expert_filled.csv`, `why_stopped_retest_original.csv`, `why_stopped_retest_corrected_documented.csv` | private | the filled-in workbooks exported to CSV (same columns as the *Review* sheet, incl. the registry text) |
| `why_stopped_review_KEY_do_not_open_before_review.csv` | private | `review_id`, `nct_id`, `stratum`, `inclusion_prob`, `weight` and the rules-v1 output incl. `matched_keywords`, `negated_mentions` (registry quotes) |
| `why_stopped_holdout_KEY_do_not_open_before_review.csv` | private | `review_id`, `nct_id`, `selection`, rules v1/v2 labels and safety flags |
| `why_stopped_second_rater_KEY_do_not_open_before_review.csv` | private | `rater2_id` (= `retest_id`), `review_id`, `nct_id`, `expert` (first-round label of the main review) |
