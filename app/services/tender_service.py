from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis import get_tender as get_tender_cache, invalidate_tender, set_tender
from app.models.tender import Tender, TenderStatus, TenderStatusHistory
from app.schemas.tender import TenderCreate, TenderUpdateStatus

ALLOWED_TRANSITIONS = {
    TenderStatus.draft: {TenderStatus.active},
    TenderStatus.active: {TenderStatus.won, TenderStatus.lost},
    TenderStatus.won: set(),
    TenderStatus.lost: set(),
}


async def create_tender(session: AsyncSession, data: TenderCreate) -> Tender:
    tender = Tender(title=data.title, description=data.description)
    session.add(tender)
    await session.commit()
    await session.refresh(tender)
    return tender


async def get_tender(session: AsyncSession, tender_id: int) -> Tender | None:
    result = await session.execute(select(Tender).where(Tender.id == tender_id))
    return result.scalar_one_or_none()


async def get_tender_cached(session: AsyncSession, tender_id: int) -> dict | None:
    cached = await get_tender_cache(tender_id)
    if cached is not None:
        return cached
    tender = await get_tender(session, tender_id)
    if tender is None:
        return None
    data = {
        "id": tender.id,
        "title": tender.title,
        "description": tender.description,
        "status": tender.status,
        "created_at": tender.created_at.isoformat(),
        "updated_at": tender.updated_at.isoformat(),
    }
    await set_tender(tender_id, data)
    return data


async def update_status(session: AsyncSession, tender_id: int, data: TenderUpdateStatus) -> Tender | None:
    tender = await get_tender(session, tender_id)
    if tender is None:
        return None
    current = TenderStatus(tender.status)
    if data.new_status not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(
            f"invalid transition from {current.value} to {data.new_status.value}"
        )
    history = TenderStatusHistory(
        tender_id=tender.id,
        old_status=tender.status,
        new_status=data.new_status.value,
        changed_by=data.changed_by,
        reason=data.reason,
    )
    session.add(history)
    tender.status = data.new_status.value
    await session.commit()
    await session.refresh(tender)
    await invalidate_tender(tender_id)
    return tender


async def get_history(session: AsyncSession, tender_id: int) -> list[TenderStatusHistory]:
    result = await session.execute(
        select(TenderStatusHistory)
        .where(TenderStatusHistory.tender_id == tender_id)
        .order_by(TenderStatusHistory.changed_at)
    )
    return list(result.scalars())
