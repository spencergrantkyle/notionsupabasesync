"""Field mapping and conflict resolution logic."""
from datetime import datetime
from typing import Dict


def choose_newer(supabase_ts: str, notion_ts: str) -> str:
    """Return which side is newer based on ISO timestamps."""
    supabase_time = datetime.fromisoformat(supabase_ts)
    notion_time = datetime.fromisoformat(notion_ts)
    return "supabase" if supabase_time >= notion_time else "notion"
