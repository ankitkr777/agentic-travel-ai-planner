def format_currency(amount: float) -> str:
    try: return f"${amount:,.2f}"
    except Exception: return "$0.00"

def format_itinerary_html(plan_json: str) -> str:
    return f"<html><body><h1>Travel Plan</h1><pre>{plan_json}</pre></body></html>"   