"""Rule-based why_stopped classifier (rules v2) – copy of notebook 03, section 1.

Notebook 03 is the reference; this module only makes the same rules reusable in later notebooks
(e.g. notebook 07, cross-registry comparison). Notebook 07 checks that it reproduces the stored
v2 labels exactly.
"""
import re
from pathlib import Path

import pandas as pd

_MAPPINGS = Path(__file__).resolve().parent.parent / "mappings"
keywords = pd.read_csv(_MAPPINGS / "why_stopped_keywords.csv")

CATEGORIES = ["Safety", "Efficacy/Futility", "COVID-19", "Recruitment", "Funding", "Strategic/Business",
              "Sponsor decision (unspecified)", "Other", "Not stated"]
# Priority for the single primary reason (medically most relevant first; COVID-19 before
# recruitment/business because it is usually the root cause of those problems)
PRIMARY_PRIORITY = CATEGORIES

NEGATION_CUE = re.compile(r"\b(no|not|non|none|neither|nor|without|unrelated|never|nothing)\b|n't\b")
CAUSAL = re.compile(r"\b(due to|because|owing to|as a result of|based on|following|caused by|given|for|since)\b")
CLAUSE_SPLIT = re.compile(r"[.;!?\n]|:(?=\s)|\bbut\b|\bhowever\b|\balthough\b|\bwhereas\b|\binstead\b|\brather\b")
UNINFORMATIVE = re.compile(
    r"^(the )?(study|trial)?\s*(was |has been |is )?(terminated|stopped|ended|closed|discontinued|halted)?"
    r"\s*(early|prematurely)?\s*(by sponsor)?$|^(early )?termination$"
    r"|^(n/?a|na|none|other|unknown)$|^see .{0,40}(above|below|description)$")

# v2 (after expert validation)
TERMINATION_WORDS = re.compile(r"((being|been|is|was|were|the|study|trial|terminated|stopped|discontinued|halted|"
                               r"closed|ended|prematurely|early)\s*)+")
NEUTRAL_SAFETY_CONTEXT = re.compile(
    r"\b(characteri[sz]\w*|sufficient\w*|enough|acceptable|manageable|adequate\w*|well[- ]established|"
    r"established|consistent|collected|demonstrated|no need|unchanged|reassuring|analy[sz]e|analysis of|"
    r"followed up|follow[- ]?up|f-?up|improv\w*)\b")

PATTERNS = [(r.category, re.compile(r.pattern, re.I), r.flag if isinstance(r.flag, str) else None, r.pattern)
            for r in keywords.itertuples()]


def is_negated(clause, match_start):
    """True if a negation cue before the match (in the same clause) still applies to it."""
    before = clause[:match_start]
    cues = list(NEGATION_CUE.finditer(before))
    if not cues:
        return False
    between = before[cues[-1].end():]
    causal = CAUSAL.search(between)
    # A causal connector after at least one other word ends the scope of the negation:
    # "not proceeding to phase 2 due to safety"  -> not negated
    # "not due to safety"                         -> negated
    if causal:
        words_before = between[:causal.start()].strip()
        # v2: words that only describe the termination itself keep the negation alive:
        # "not terminated due to a safety reason" / "is not being terminated for safety"
        if words_before and not TERMINATION_WORDS.fullmatch(words_before):
            return False
    return True


def neutral_safety(clause, matched_text, flag):
    """v2: generic safety / tolerability / benefit-risk wording used as information, not as a reason."""
    generic = re.fullmatch(r"safety|tolerability", matched_text.strip()) or flag == "benefit_risk"
    return bool(generic and NEUTRAL_SAFETY_CONTEXT.search(clause))


def classify(text):
    result = {c: 0 for c in CATEGORIES}
    flags, hits, negated = set(), [], []
    if not isinstance(text, str) or not text.strip():
        result["Not stated"] = 1
        return result, flags, hits, negated
    clean = re.sub(r"\s+", " ", text.lower().replace("\\&", "&")).strip()
    # "non-clinical" and "non-favorable" are not negations of the following keyword
    clean = re.sub(r"\bnon[- ]?clinical\b", "nonclinical", clean)
    clean = re.sub(r"\bnon[- ]?favou?rable\b", "unfavorable", clean)
    if UNINFORMATIVE.match(clean.rstrip(". ")):
        result["Not stated"] = 1
        return result, flags, ["uninformative text"], negated

    for clause in CLAUSE_SPLIT.split(clean):
        for category, pattern, flag, raw in PATTERNS:
            for m in pattern.finditer(clause):
                if is_negated(clause, m.start()):
                    negated.append(f"{category}: '{m.group(0)}'")
                    continue
                if category == "Safety" and neutral_safety(clause, m.group(0), flag):
                    negated.append(f"Safety (information, not a reason): '{m.group(0)}'")
                    continue
                result[category] = 1
                hits.append(f"{category}: '{m.group(0)}'")
                if flag:
                    flags.add(flag)

    # "Sponsor decision" counts only if no other substantive reason was found
    substantive = [c for c in CATEGORIES if c not in ("Sponsor decision (unspecified)", "Not stated") and result[c]]
    if result["Sponsor decision (unspecified)"] and substantive:
        result["Sponsor decision (unspecified)"] = 0
    if not any(result.values()):
        result["Other"] = 1
        flags.add("unmatched")
    return result, flags, hits, negated


def primary_reason(result):
    return next(c for c in PRIMARY_PRIORITY if result[c])
