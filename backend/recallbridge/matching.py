from __future__ import annotations

import re
from difflib import SequenceMatcher

from .models import MatchRequest, RecallMatch, RecallRecord


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def words(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if len(token) > 1
    }


def text_similarity(left: str, right: str) -> float:
    if not left.strip() or not right.strip():
        return 0.0
    sequence = SequenceMatcher(None, left.lower(), right.lower()).ratio()
    left_words = words(left)
    right_words = words(right)
    union = left_words | right_words
    overlap = len(left_words & right_words) / len(union) if union else 0.0
    return max(sequence, overlap)


def score_recall(request: MatchRequest, recall: RecallRecord) -> RecallMatch | None:
    reasons: list[str] = []
    score = 0
    exact_identifier = False
    requested_identifiers = {
        "upc": request.upc,
        "model": request.model,
        "lot": request.lot,
    }

    for identifier in recall.identifiers:
        requested = requested_identifiers.get(identifier.kind.lower(), "")
        if requested and normalize(requested) == normalize(identifier.value):
            exact_identifier = True
            score = max(score, 100)
            reasons.append(f"Exact {identifier.kind.upper()} match")

    searchable = " ".join(
        [recall.title, recall.product_description, recall.manufacturer]
    )
    name_score = text_similarity(request.product_name, searchable)
    if name_score >= 0.25:
        score = max(score, round(name_score * 78))
        reasons.append("Product name resembles the recall description")

    brand_score = text_similarity(request.brand, recall.manufacturer)
    if request.brand and brand_score >= 0.35:
        score = min(99, score + round(brand_score * 18))
        reasons.append("Brand or manufacturer is similar")

    for kind, requested in requested_identifiers.items():
        if not requested or exact_identifier:
            continue
        if normalize(requested) in normalize(searchable):
            score = max(score, 72)
            reasons.append(f"{kind.title()} appears in recall text")

    if request.category and request.category == recall.category:
        score = min(100, score + 4)

    if score < 30:
        return None

    confidence = "exact" if exact_identifier else "strong" if score >= 72 else "possible"
    return RecallMatch(
        recall=recall,
        confidence=confidence,
        score=score,
        reasons=reasons or ["General text similarity"],
    )


def find_matches(
    request: MatchRequest,
    recalls: list[RecallRecord],
) -> list[RecallMatch]:
    matches = [
        match
        for recall in recalls
        if (not request.category or recall.category == request.category)
        if (match := score_recall(request, recall)) is not None
    ]
    return sorted(matches, key=lambda match: match.score, reverse=True)[:10]
