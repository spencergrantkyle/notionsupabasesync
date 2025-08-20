from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Notion ↔ Supabase Sync Service")

class ChangeEvent(BaseModel):
    type: str
    record: dict

@app.post("/supabase-change/{secret}")
async def supabase_change(secret: str, event: ChangeEvent):
    # TODO: verify secret and handle event
    return {"status": "received", "secret": secret, "type": event.type}

@app.post("/sync/notion-poll")
async def notion_poll():
    # TODO: poll Notion for updates and sync to Supabase
    return {"status": "ok"}
