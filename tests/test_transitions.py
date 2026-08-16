from app.models.tender import TenderStatus
from app.services.tender_service import ALLOWED_TRANSITIONS


def test_draft_can_go_to_active():
    assert TenderStatus.active in ALLOWED_TRANSITIONS[TenderStatus.draft]


def test_draft_cannot_go_to_won():
    assert TenderStatus.won not in ALLOWED_TRANSITIONS[TenderStatus.draft]


def test_active_can_go_to_won_and_lost():
    assert ALLOWED_TRANSITIONS[TenderStatus.active] == {
        TenderStatus.won,
        TenderStatus.lost,
    }


def test_won_is_terminal():
    assert ALLOWED_TRANSITIONS[TenderStatus.won] == set()


def test_lost_is_terminal():
    assert ALLOWED_TRANSITIONS[TenderStatus.lost] == set()
