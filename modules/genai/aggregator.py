# modules/genai/aggregator.py

def aggregate_scores(
    fraud_score: float,
    tamper_score: float,
    ml_fake_prob: float,
    retrieval_score: float,
    llm_risk: str
):
    """
    Combines traditional ML + Forensics + GenAI.
    Score 0 = trustworthy, 100 = highly fake.
    """

    llm_penalty = {
        "low": 5,
        "medium": 20,
        "high": 40
    }.get(llm_risk.lower(), 10)

    final = (
        fraud_score * 0.25 +
        tamper_score * 0.25 +
        ml_fake_prob * 40 +
        retrieval_score * 10 +
        llm_penalty
    )

    return min(max(0, final), 100)
