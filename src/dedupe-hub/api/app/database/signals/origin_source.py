from sqlalchemy import event
from app.config import settings
from app.database.models.facility_match import FacilityMatch
from app.database.models.facility import Facility
from app.database.models.extended_field import ExtendedField

models = [FacilityMatch, Facility, ExtendedField]

for model in models:
    @event.listens_for(model, 'before_insert')
    def set_origin_source(mapper, connection, target):
        target.origin_source = settings.instance_source or 'os_hub'