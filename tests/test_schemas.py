import pytest
from pydantic import ValidationError

from app.schemas.tender import TenderCreate, TenderUpdateStatus


def test_create_schema_defaults():
    data = TenderCreate(title="test")
    assert data.title == "test"
    assert data.description == ""


def test_create_schema_rejects_empty_title():
    with pytest.raises(ValidationError):
        TenderCreate(title="")


def test_update_status_schema_rejects_empty_changed_by():
    with pytest.raises(ValidationError):
        TenderUpdateStatus(new_status="active", changed_by="")
