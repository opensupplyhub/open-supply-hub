from app.database.sqlalchemy import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from geoalchemy2 import Geometry

class HistoricalFacilityMatch(Base):
    __tablename__ = 'api_historicalfacilitymatch'

    # These mirror `api_facilitymatch`: `id` is that table's integer primary
    # key and `facility_id` is an OS ID string. They were declared the other
    # way round, which is harmless while these columns are only ever compared
    # in SQL, but silently coerces the moment either is compared to a Python
    # value.
    id = Column(Integer, primary_key=True)
    facility_id = Column(String, nullable=False)
    history_id = Column(Integer, nullable=False)
    history_type = Column(String, nullable=False)