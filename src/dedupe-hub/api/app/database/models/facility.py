from app.database.sqlalchemy import Base
from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String
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
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())
