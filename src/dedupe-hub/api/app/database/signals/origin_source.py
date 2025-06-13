from sqlalchemy import event
from app.config import settings
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility import Facility
from sqlalchemy.orm import configure_mappers

configure_mappers()

models = [FacilityMatch, Facility]

for model in models:
    @event.listens_for(model, 'before_insert')
    def set_origin_source(mapper, connection, target):
        if not target.origin_source:
            target.origin_source = settings.instance_source or 'os_hub'