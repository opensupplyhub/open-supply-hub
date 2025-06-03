from app.database.sqlalchemy import Base
from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func


class FacilityListItem(Base):
    UPLOADED = 'UPLOADED'
    PARSED = 'PARSED'
    DUPLICATE = 'DUPLICATE'
    GEOCODED = 'GEOCODED'
    GEOCODED_NO_RESULTS = 'GEOCODED_NO_RESULTS'
    MATCHED = 'MATCHED'
    POTENTIAL_MATCH = 'POTENTIAL_MATCH'
    CONFIRMED_MATCH = 'CONFIRMED_MATCH'
    ERROR = 'ERROR'
    ERROR_PARSING = 'ERROR_PARSING'
    ERROR_GEOCODING = 'ERROR_GEOCODING'
    ERROR_MATCHING = 'ERROR_MATCHING'
    DELETED = 'DELETED'
    ITEM_REMOVED = 'ITEM_REMOVED'

    __tablename__ = 'api_facilitylistitem'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, nullable=False)
    row_index = Column(Integer, nullable=False)
    raw_data = Column(String, nullable=True)
    status = Column(String, nullable=False, default='UPLOADED')
    processing_started_at = Column(TIMESTAMP(timezone=True),
                                nullable=False)
    processing_completed_at = Column(TIMESTAMP(timezone=True),
                                nullable=False)
    processing_results = Column(JSONB)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    geocoded_point = Column(Geometry('POINT'))
    sector = Column(ARRAY(Integer), nullable=False)
    geocoded_address = Column(String, nullable=False)
    facility_id = Column(String, ForeignKey('api_facility.id'), nullable=True)
    clean_name = Column(String, nullable=False)
    clean_address = Column(String, nullable=False)
    origin_source = Column(String, nullable=False, default="os_hub")
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())
