from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias


def os_id_exists_here(os_id):
    """
    Whether this instance knows the identifier, following a merge.

    A superseded OS ID keeps resolving to the surviving location through
    FacilityAlias, so an identifier that has been merged away is still
    present here. Resolution follows the alias on read, which is the
    behaviour scope doc 2.7 promises.

    Shared on purpose. The read side returns 404 for an identifier that is
    not here (3.4) and the write side returns 404 or 422 for the same
    condition (3.2). Those answers have to agree about what "here" means, so
    they ask the same question rather than each implementing it.
    """
    if Facility.objects.filter(pk=os_id).exists():
        return True
    return FacilityAlias.objects.filter(pk=os_id).exists()
