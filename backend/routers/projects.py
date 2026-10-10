from fastapi import APIRouter

router = APIRouter(tags=["Projects"])


@router.get("/projects")
async def stub() -> dict:
    return {"status": "stub"}
