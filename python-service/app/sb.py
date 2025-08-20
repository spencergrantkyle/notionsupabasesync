"""Supabase REST helpers.

These functions wrap calls to the Supabase REST API. They are
placeholders and should be implemented with real HTTP requests.
"""
from typing import Any, Dict

import httpx

async def upsert_item(client: httpx.AsyncClient, item: Dict[str, Any]) -> Dict[str, Any]:
    """Upsert an item into Supabase.

    Args:
        client: An authenticated httpx.AsyncClient.
        item: The row data to upsert.

    Returns:
        The created or updated row.
    """
    # TODO: implement Supabase REST call
    return item
