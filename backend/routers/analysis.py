from fastapi import APIRouter

router = APIRouter(tags=["Analysis"])


@router.get("/analysis")
async def stub() -> dict:
    return {"status": "stub"}
