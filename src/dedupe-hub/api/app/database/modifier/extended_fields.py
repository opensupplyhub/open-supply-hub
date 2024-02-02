from app.database.models.extended_field import ExtendedField
from app.database.sqlalchemy import get_session

def update_extendedfields_for_list_item(list_item):
    with get_session() as session:
        for extended_field in session.query(ExtendedField).filter(ExtendedField.facility_list_item_id == list_item.id):
            extended_field.facility_id = list_item.facility_id
            session.commit()

        session.close()