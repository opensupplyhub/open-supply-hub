from app.database.sqlalchemy import Base
from geoalchemy2 import Geometry
from sqlalchemy import (
    TIMESTAMP, Boolean, Column, Float, ForeignKey, Integer, String
)
from sqlalchemy.sql import func


class Facility(Base):
    __tablename__ = 'api_facility'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    location = Column(Geometry('POINT'))
    created_from_id = Column(Integer, ForeignKey('api_facilitylistitem.id'), nullable=False)
    is_closed = Column(Boolean, nullable=True)
    new_os_id = Column(String, nullable=True)
    has_inexact_coordinates = Column(Boolean, nullable=False, default=False)
    origin_source = Column(String, nullable=True)
    # Earth Genome candidate columns (OSDEV-3242, Django migration 0237).
    # Mirrors api/models/facility/facility.py. `default` is set explicitly
    # so a facility dedupe-hub creates for an unmatched list item is always
    # written as a confirmed (non-candidate) facility; candidates are only
    # ever created by the candidate ingest pipeline on the Django side.
    is_candidate = Column(Boolean, nullable=False, default=False)
    polygon = Column(Geometry('POLYGON', srid=4326), nullable=True)
    confidence = Column(Float, nullable=True)
    external_id = Column(String, nullable=True)
    source = Column(String, nullable=False, default='')
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())
