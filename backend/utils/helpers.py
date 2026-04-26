import json

def dict_to_json_string(data: dict) -> str:
    try: return json.dumps(data, indent=2)
    except TypeError as e: raise ValueError(f"Failed to serialize dict to JSON: {e}")

def json_string_to_dict(data: str) -> dict:
    try: return json.loads(data)
    except json.JSONDecodeError as e: raise ValueError(f"Invalid JSON string provided: {e}")