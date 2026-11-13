"""Import of the domain expert's blinded review (Block 10).

The review was filled in with short codes (Numbers does not support the drop-down lists).
Full category names are accepted as well. Every row is validated; invalid entries are
reported with their review_id instead of being silently dropped.
"""
import re
import unicodedata

import pandas as pd

CATEGORY_CODES = {
    "S": "Safety",
    "E": "Efficacy/Futility",
    "C": "COVID-19",
    "R": "Recruitment",
    "F": "Funding",
    "B": "Strategic/Business",
    "D": "Sponsor decision (unspecified)",
    "O": "Other",
    "N": "Not stated",
}
YES_NO_CODES = {"Y": "yes", "YES": "yes", "N": "no", "NO": "no"}
FULL_NAMES = {name.lower(): name for name in CATEGORY_CODES.values()}

COLUMNS = {
    "review_id": "review_id",
    "expert_primary_category": "expert_primary",
    "expert_safety_related": "expert_safety_related",
    "expert_other_categories": "expert_other",
    "comment": "expert_comment",
}


def _normalise(value):
    """Strip whitespace and diacritics (e.g. 'Ń' -> 'N'), so typing variants are accepted."""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text).strip()


def _to_category(value):
    """Map a code (S, E, …) or a full category name to the full name; None if invalid."""
    text = _normalise(value)
    return CATEGORY_CODES.get(text.upper()) or FULL_NAMES.get(text.lower())


def _find_review_sheet(path):
    """Return the sheet that contains the 'review_id' header (sheet names may change on export)."""
    sheets = pd.read_excel(path, sheet_name=None)
    for name, df in sheets.items():
        if any(str(c).strip().lower() == "review_id" for c in df.columns):
            return df
    raise ValueError("No sheet with a 'review_id' column found")


def load_review(path, expected_ids):
    """Read, convert and validate the review file. Returns (review, problems)."""
    if str(path).lower().endswith(".csv"):
        raw = pd.read_csv(path)
    else:
        raw = _find_review_sheet(path)

    # Match columns by prefix, so that headers such as 'expert_safety_related (yes/no)' work
    rename = {}
    for col in raw.columns:
        key = re.sub(r"\s*\(.*\)$", "", str(col)).strip().lower()
        for prefix, target in COLUMNS.items():
            if key.startswith(prefix):
                rename[col] = target
    df = raw.rename(columns=rename)
    missing_cols = [c for c in COLUMNS.values() if c not in df.columns and c not in ("expert_other", "expert_comment")]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    for optional in ("expert_other", "expert_comment"):
        if optional not in df.columns:
            df[optional] = None

    df = df.dropna(subset=["review_id"]).copy()
    df["review_id"] = df["review_id"].astype(int)
    problems = []

    # Completeness: every expected review_id exactly once
    ids = df["review_id"].tolist()
    for rid in sorted(set(expected_ids) - set(ids)):
        problems.append((rid, "row missing"))
    for rid in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append((rid, "review_id duplicated"))
    for rid in sorted(set(ids) - set(expected_ids)):
        problems.append((rid, "unexpected review_id"))

    primary, safety, other = [], [], []
    for r in df.itertuples():
        cat = _to_category(r.expert_primary) if pd.notna(r.expert_primary) else None
        if cat is None:
            problems.append((r.review_id, f"invalid/empty primary category: {r.expert_primary!r}"))
        primary.append(cat)

        yn = YES_NO_CODES.get(_normalise(r.expert_safety_related).upper()) if pd.notna(r.expert_safety_related) else None
        if yn is None:
            problems.append((r.review_id, f"invalid/empty safety_related: {r.expert_safety_related!r}"))
        safety.append(yn)

        cats = []
        if pd.notna(r.expert_other) and str(r.expert_other).strip():
            for part in re.split(r"[;,/]", str(r.expert_other)):
                if not part.strip():
                    continue
                c = _to_category(part)
                if c is None:
                    problems.append((r.review_id, f"invalid code in other_categories: {part.strip()!r}"))
                else:
                    cats.append(c)
        other.append("|".join(dict.fromkeys(cats)) or None)

    df["expert_primary"] = primary
    df["expert_safety_related"] = safety
    df["expert_other"] = other
    return df[["review_id", "expert_primary", "expert_safety_related", "expert_other", "expert_comment"]], problems
