from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_session
from app.schemas.tender import (
    TenderCreate,
    TenderRead,
    TenderStatusHistoryRead,
    TenderUpdateStatus,
)
from app.services import tender_service

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.post("", response_model=TenderRead, status_code=201)
async def create_tender(
    data: TenderCreate, session: AsyncSession = Depends(get_session)
):
    return await tender_service.create_tender(session, data)


@router.get("/{tender_id}", response_model=TenderRead)
async def get_tender(tender_id: int, session: AsyncSession = Depends(get_session)):
    tender = await tender_service.get_tender_cached(session, tender_id)
    if tender is None:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.patch("/{tender_id}/status", response_model=TenderRead)
async def update_status(
    tender_id: int,
    data: TenderUpdateStatus,
    session: AsyncSession = Depends(get_session),
):
    try:
        tender = await tender_service.update_status(session, tender_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if tender is None:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender


@router.get("/{tender_id}/history", response_model=list[TenderStatusHistoryRead])
async def get_history(tender_id: int, session: AsyncSession = Depends(get_session)):
    history = await tender_service.get_history(session, tender_id)
    return history
