from app.database.sqlalchemy import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, Boolean
from sqlalchemy.sql import func

class Contributor(Base):
    __tablename__ = 'api_contributor'

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    website = Column(String, nullable=False)
    contrib_type = Column(String, nullable=False)
    other_contrib_type = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_notes = Column(String, nullable=False)
    embed_config_id = Column(Integer, nullable=False)
    embed_level = Column(Integer, nullable=False)
    match_responsibility = Column(String, nullable=False, default="moderator")
    origin_source = Column(String, nullable=True, blank=True)
    created_at = Column(TIMESTAMP(timezone=True),
                       nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),
                       default=None, onupdate=func.now())