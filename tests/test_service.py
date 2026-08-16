from unittest.mock import AsyncMock

import pytest

from app.models.tender import Tender, TenderStatus
from app.schemas.tender import TenderUpdateStatus
from app.services import tender_service


class FakeSession:
    def __init__(self, tender):
        self.tender = tender
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

    async def execute(self, stmt):
        return FakeResult(self.tender)


class FakeResult:
    def __init__(self, tender):
        self.tender = tender

    def scalar_one_or_none(self):
        return self.tender


async def test_update_status_valid(monkeypatch):
    tender = Tender(id=1, title="test", status=TenderStatus.draft.value)
    session = FakeSession(tender)
    monkeypatch.setattr(tender_service, "invalidate_tender", AsyncMock())
    data = TenderUpdateStatus(
        new_status=TenderStatus.active, changed_by="denis", reason="go"
    )

    result = await tender_service.update_status(session, 1, data)

    assert result.status == TenderStatus.active.value
    assert session.added[0].new_status == TenderStatus.active.value
    assert session.added[0].old_status == TenderStatus.draft.value
    assert session.added[0].changed_by == "denis"


async def test_update_status_invalid_transition(monkeypatch):
    tender = Tender(id=1, title="test", status=TenderStatus.won.value)
    session = FakeSession(tender)
    monkeypatch.setattr(tender_service, "invalidate_tender", AsyncMock())
    data = TenderUpdateStatus(new_status=TenderStatus.lost, changed_by="denis")

    with pytest.raises(ValueError):
        await tender_service.update_status(session, 1, data)


async def test_update_status_not_found():
    session = FakeSession(None)
    data = TenderUpdateStatus(new_status=TenderStatus.active, changed_by="denis")

    result = await tender_service.update_status(session, 1, data)

    assert result is None
