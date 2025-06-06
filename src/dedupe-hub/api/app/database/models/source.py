from app.database.sqlalchemy import Base
from sqlalchemy import TIMESTAMP, Column, Integer, Boolean, String
from sqlalchemy.sql import func

class Source(Base):
    __tablename__ = 'api_source'

    id = Column(Integer, primary_key=True)
    contributor_id = Column(Integer, nullable=False)
    facility_list_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    create = Column(Boolean, nullable=False, default=True)
    origin_source = Column(String, nullable=True, blank=True)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())