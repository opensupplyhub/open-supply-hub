from app.database.sqlalchemy import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from geoalchemy2 import Geometry

class HistoricalFacilityMatch(Base):
    __tablename__ = 'api_historicalfacilitymatch'

    id = Column(String, primary_key=True)
    facility_id = Column(Integer, nullable=False)
    history_id = Column(Integer, nullable=False)
    history_type = Column(String, nullable=False)