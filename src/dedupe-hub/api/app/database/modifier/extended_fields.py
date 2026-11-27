from app.database.models.extended_field import ExtendedField


def update_extendedfields_for_list_item(session, list_item_id, facility_id):
    """
    Point the list item's extended fields at the facility it was matched to.
    Runs in the caller's session so the change commits with the item's match
    rows and status.
    """
    session.query(ExtendedField). \
        filter(ExtendedField.facility_list_item_id == list_item_id). \
        update({ExtendedField.facility_id: facility_id},
               synchronize_session=False)
