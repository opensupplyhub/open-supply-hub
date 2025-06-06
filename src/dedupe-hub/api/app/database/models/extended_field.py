from app.database.sqlalchemy import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database.models.facility import Facility
from app.database.models.facility_list_item import FacilityListItem
from app.database.models.facility_claim import FacilityClaim

class ExtendedField(Base):
    __tablename__ = 'api_extendedfield'

    id = Column(Integer, primary_key=True)
    contributor_id = Column(Integer, nullable=False)
    facility_id = Column(String, ForeignKey(Facility.id), nullable=True)
    facility_list_item_id = Column(Integer, ForeignKey(FacilityListItem.id), nullable=True)
    facility_claim_id = Column(Integer, ForeignKey(FacilityClaim.id), nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    field_name = Column(String, nullable=False)
    value = Column(JSONB)
    origin_source = Column(String, nullable=False, default="os_hub")
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())