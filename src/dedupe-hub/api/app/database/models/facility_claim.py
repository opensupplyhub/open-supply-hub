from app.database.sqlalchemy import Base
from sqlalchemy import Column, Integer

class FacilityClaim(Base):
    __tablename__ = 'api_facilityclaim'

    id = Column(Integer, primary_key=True)