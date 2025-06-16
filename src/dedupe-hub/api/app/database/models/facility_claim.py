from app.database.sqlalchemy import Base
from sqlalchemy import Column, Integer, String

class FacilityClaim(Base):
    __tablename__ = 'api_facilityclaim'

    id = Column(Integer, primary_key=True)
    origin_source = Column(String, nullable=True)
