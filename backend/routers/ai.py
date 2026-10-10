from fastapi import APIRouter

router = APIRouter(tags=["AI"])


@router.get("/ai")
async def stub() -> dict:
    return {"status": "stub"}
