from app.database.sqlalchemy import Base
from sqlalchemy import Column, String, Integer

class HistoricalFacility(Base):
    __tablename__ = 'api_historicalfacility'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    history_id = Column(Integer, nullable=False)
    history_type = Column(String, nullable=False)