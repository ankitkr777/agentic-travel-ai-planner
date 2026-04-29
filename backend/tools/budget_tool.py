from langchain.tools import tool

@tool
async def calculate_optimal_budget(total_budget: float) -> dict:
    """Allocates budget optimally."""
    try:
        return {"lodging": total_budget * 0.40, "food": total_budget * 0.30, "activities": total_budget * 0.20, "misc": total_budget * 0.10}
    except Exception as e:
        return {"error": str(e)}