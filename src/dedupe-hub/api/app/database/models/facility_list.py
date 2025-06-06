from app.database.sqlalchemy import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer
from sqlalchemy.sql import func

class FacilityList(Base):
    __tablename__ = 'api_facilitylist'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_name = Column(String, nullable=False)
    header = Column(String, nullable=False)
    replaces_id = Column(Integer, nullable=False)
    match_responsibility = Column(String, nullable=False, default="moderator")
    file = Column(String, nullable=True)
    origin_source = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())