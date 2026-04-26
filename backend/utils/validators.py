def validate_budget(budget: float) -> bool:
    if budget is None or budget <= 0: raise ValueError("Budget must be positive.")
    return True