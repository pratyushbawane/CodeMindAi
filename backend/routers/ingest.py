from fastapi import APIRouter

router = APIRouter(tags=["Ingest"])


@router.get("/ingest")
async def stub() -> dict:
    return {"status": "stub"}
