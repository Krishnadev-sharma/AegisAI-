def compute_compliance_score(assessment) -> int:
    """
    Compute a 0-100 compliance score from sub-scores.

    Weights:
      data_governance: 25%
      transparency: 25%
      human_oversight: 25%
      robustness: 25%

    Missing sub-scores are treated as 0.
    """

    weights = {
        "data_governance_score": 0.25,
        "transparency_score": 0.25,
        "human_oversight_score": 0.25,
        "robustness_score": 0.25,
    }

    total = sum(
        (getattr(assessment, field, 0) or 0) * weight
        for field, weight in weights.items()
    )

    return round(total)