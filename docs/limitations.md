# Limitations

<!-- Collected during the project; summarised in the README at the end. -->

- **Registration bias:** Phase I trials were often not subject to mandatory registration
  (ClinicalTrials.gov: exempt from FDAAA 801; EU: adult non-PIP Phase I trials not public
  under Directive 2001/20/EC). Results apply to *registered* trials only.
- **EudraCT coverage:** Phase-I-only trials in adults outside a PIP are practically not
  public (4 of 2,823 visible); the EU CTR mainly shows paediatric/PIP and combined Phase I/II
  trials. Only 3.9 % of adult Phase 1 trials registered on ClinicalTrials.gov with a EudraCT
  number appear in the EU CTR Phase I download (0/40 in a full-register spot check). EudraCT
  termination shares therefore describe a different study mix and are not directly comparable
  with ClinicalTrials.gov.
- **EudraCT definition:** the share of prematurely ended trials is 31.9 % (any country, D21) vs.
  17.8 % (all reporting countries, D22); both are reported.
- **EudraCT status:** status is reported per member state; one trial-level status is
  derived with a priority rule (D21). UK records show only "GB – no longer in EU/EEA".
  No termination reason is available in the protocol data.
- **CTIS coverage:** only a few years of data → descriptive comparison only.
- **CTIS:** data from 2022/2023 only, many trials still running → early-terminated trials are
  over-represented among ended trials; transitioned trials are a selected group (still
  running on 30 Jan 2025). The coded termination reason is dominated by "Sponsor decision".
- **CTIS data access:** CTIS data were retrieved via the portal's public search interface
  (not a documented API; endpoints `/ctis-public-api/search` and
  `/ctis-public-api/retrieve/{ctNumber}`), downloaded on **28 October 2026**. The interface
  may change over time; a later download may give different results. Terms of use: see
  `docs/data_sources_and_terms.md`.
- **Right-censoring in young data (CTIS, ClinicalTrials.gov 2020–2022):** among recently
  started trials, short trials (often in healthy volunteers) have already ended, while
  longer patient trials are often still running. Early termination shares among *ended*
  trials are therefore biased upwards for long trials, and group comparisons (e.g. healthy
  volunteers vs. patients) must not be shown without this caveat.
- **Selective (retrospective) registration:** 10.6 % of completed but only 2.7 % of
  terminated trials were registered after their primary completion date. Successful trials
  are more likely to be registered retrospectively, while terminated trials that were never
  registered remain invisible. The **true termination share of Phase I trials is therefore
  probably higher** than the share visible in the registry.
- **Termination-reason classification:** rule-based, validated blinded by **one** domain expert
  (no second rater → no inter-rater agreement). Reliability is limited to an intra-rater
  test-retest on 50 texts re-rated by the same expert after only a few days (kappa 0.78 for the
  primary reason, 0.96 for safety yes/no) – a **memory effect** is possible and would inflate agreement. Two labels were corrected by the expert after
  unblinding (documented; metrics reported before and after correction). Safety estimates are robust (all
  algorithm-Safety texts reviewed); estimates for the other categories rest on 60 random texts
  (weight 14.4 each) and are uncertain – e.g. Efficacy/Futility 9.4 % (algorithm v1) vs. 15.3 %
  (weighted expert estimate). Rule version v2 was revised using the validation sample; the
  official accuracy is therefore reported for v1.
- **CTIS coded termination reason:** only a coded reason per member state, no free text. "Sponsor
  Decision" is the only code in 79 % of early-terminated trials, and there is no code for
  efficacy/futility → CTIS cannot answer *why* trials stop. Same-trial comparison with
  ClinicalTrials.gov uses rule-based labels without expert review.
- **CTIS publication delays:** for adult Phase I (Category 1) trials, most structured data, the
  protocol and the results are published only 30 months after the end of the trial; documents of
  trials submitted before 18 June 2024 are not published. Our CTIS data therefore contain less
  detail for adult Phase I trials than for other categories.
- **Cross-registry linkage:** IDs are incomplete in both directions (52 % of CTIS Phase I trials
  linked to an NCT number; healthy-volunteer trials only 24 %). ClinicalTrials.gov → CTIS links come
  only from trials with a site in the 7 target countries. Statuses differ between registries
  (EU-specific vs. global, different update times).
- **EU CTR results:** availability is measured at the download date (80 % where due), not whether
  results were posted within the 12-/6-month deadline.
- **ClinicalTrials.gov coverage of European healthy-volunteer trials:** in CTIS only 24 % of the
  healthy-volunteer Phase I trials (287 of 1,210) carry or are linked to an NCT number (patient
  trials: 67 %). The ClinicalTrials.gov data set therefore covers European healthy-volunteer
  trials only partially; results for healthy volunteers describe the trials registered on
  ClinicalTrials.gov, not all European healthy-volunteer trials.

