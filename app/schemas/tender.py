from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.tender import TenderStatus


class TenderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""


class TenderUpdateStatus(BaseModel):
    new_status: TenderStatus
    changed_by: str = Field(min_length=1, max_length=255)
    reason: str | None = None


class TenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TenderStatus
    created_at: datetime
    updated_at: datetime


class TenderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tender_id: int
    old_status: TenderStatus | None
    new_status: TenderStatus
    changed_by: str
    reason: str | None
    changed_at: datetime
