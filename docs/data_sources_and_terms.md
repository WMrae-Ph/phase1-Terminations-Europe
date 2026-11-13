# Data sources and terms of use

Checked on 28 October 2026. This is a documentation note for an independent, non-commercial
portfolio analysis, not legal advice.

## CTIS – euclinicaltrials.eu

- **Operator:** EMA maintains the website in collaboration with the EU Member States, EEA
  countries and the European Commission ("About this website").
- **Own terms of use / legal notice:** none found on euclinicaltrials.eu (pages checked:
  home, "About this website", "Data protection and privacy", cookies; `/legal-notice/`,
  `/terms-of-use/`, `/disclaimer/` return 404). No `robots.txt` (HTTP 404). No statement
  restricting automated access was found.
- **Applicable notice:** the EMA Legal Notice (https://www.ema.europa.eu/en/about-us/about-website/legal-notice):
  - information and documents on EMA web pages are public and *"may be reproduced and/or
    distributed, totally or in part, … for non-commercial and commercial purposes, provided
    that EMA is always acknowledged as the source"*; the acknowledgement must be included in
    each copy;
  - permissions do **not** cover content supplied by third parties (e.g. documents authored
    by sponsors) – this project uses only structured trial fields for aggregate statistics
    and does not republish documents;
  - the EMA logo must not be used without permission;
  - EMA accepts no liability for completeness or accuracy.
- **Access method:** public search interface of the portal (not a documented API), polite
  request rate (pause 0.3–0.5 s between requests), download date recorded.
- **Attribution used in this project:** "Source: CTIS public portal (euclinicaltrials.eu),
  European Medicines Agency, accessed 28 Oct 2026".

## EU Clinical Trials Register – clinicaltrialsregister.eu

- **Disclaimer / legal notice page:** https://www.clinicaltrialsregister.eu/disclaimer.html
  - *"In any publication or distribution of these data, you should attribute the source as
    'EU Clinical Trials Register', and clearly display the date the data were accessed."*
  - e-mail addresses from the register must not be used for marketing;
  - data are supplied by sponsors / national competent authorities; EMA is not responsible
    for completeness or accuracy; data entered before 10 March 2011 are historical and may be
    incomplete (e.g. missing end dates);
  - copyright: refers to the EMA Legal Notice (see above).
- No `robots.txt` (HTTP 404). Download via the register's own download function, pause 1.5 s.
- **Attribution used in this project:** "Source: EU Clinical Trials Register, accessed
  27 Oct 2026".

## ClinicalTrials.gov

- Accessed via the official, documented API v2.
- **Terms and Conditions** (https://clinicaltrials.gov/about-site/terms-conditions, last updated
  31 Jan 2023, checked 11 Nov 2026): data are available to all requesters at no charge; no warranty.
  *"In any publication or distribution of these data, you should:"*
  - *"Attribute the source of the data as ClinicalTrials.gov"*;
  - *"Update the data such that they are current at all times"*;
  - *"Clearly display the date the data were processed by ClinicalTrials.gov"*;
  - *"State any modifications made to the content of the data, along with a complete description
    of the modifications"*.
  Further: no proprietary rights may be asserted on the database; e-mail addresses must not be used
  for marketing; *"Some ClinicalTrials.gov data may be subject to the copyright of third parties"*;
  the terms apply *"as long as the user retains any of the data"*.
- **Attribution used in this project:** "Source: ClinicalTrials.gov API v2, data as of
  27 Oct 2026" (API data timestamp 2026-10-27T09:00:04).

## Phase 7 – what may be published? (checked 11 Nov 2026)

Not legal advice; summary of the three registries' terms for this non-commercial portfolio project.

| Material | ClinicalTrials.gov | EU CTR (EMA) | CTIS (EMA) | Decision for this project |
|---|---|---|---|---|
| **Own code** (notebooks, scripts, mappings) | not data – no restriction | – | – | publish (MIT) |
| **Aggregate result tables and figures** (shares, ORs, counts) | allowed with attribution, data date and description of modifications | allowed with attribution "EU Clinical Trials Register" + access date | allowed, EMA must be acknowledged | publish (CC BY 4.0) – attribution and dates are on every figure and in the README; modifications are described in the README (Methods), the notebooks and `docs/data_dictionary.md` |
| **Trial-level derived data** (one row per trial, e.g. NCT ID + category, registry free text such as `why_stopped`) | allowed with the same conditions, but the data should be "current at all times" – a frozen snapshot cannot meet this; free texts may carry third-party copyright | allowed with attribution | allowed; third-party (sponsor) content is not covered by the EMA permission | **do not publish** record-level registry extracts; at most NCT IDs with own labels, clearly marked as a snapshot (owner decision) |
| **Raw exports** (`data/raw`, `data/interim`) | redistribution would require keeping the data current; contains contact e-mail addresses | contains e-mail addresses (must not be used for marketing) | contains sponsor contact e-mails and sponsor documents' metadata | **do not publish** – reproducible with notebook 01 instead |
| **Validation files with registry texts** | free texts = registry content (see above) | – | – | publish only labels by NCT ID, not the texts (owner decision); keep second-rater files private |

Practical consequences:
1. Every published figure and table keeps the source line with registry name and date.
2. The README states that the data are a **snapshot** (27/28 Oct 2026) that is not updated, and points
   to the live registries – the closest feasible way to meet ClinicalTrials.gov's "current" clause
   for a static analysis.
3. Modifications are described in the README (Methods, data flow) and the notebooks.
4. No raw or trial-level registry data, no e-mail addresses, no sponsor documents are published.

