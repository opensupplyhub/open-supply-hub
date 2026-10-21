from api.models.facility.facility import Facility
from api.models.facility.facility_alias import FacilityAlias


def os_id_exists_here(os_id):
    """
    Whether this instance knows the identifier, following a merge, since
    a superseded OS ID keeps resolving through FacilityAlias. Shared by
    the read and write paths so both agree about what "here" means
    rather than each implementing it.
    """
    if Facility.objects.filter(pk=os_id).exists():
        return True
    return FacilityAlias.objects.filter(pk=os_id).exists()
