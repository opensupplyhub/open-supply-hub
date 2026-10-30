from django.db import models


class IsicCrosswalkEntry(models.Model):
    '''
    One row of the OS Hub to ISIC Rev 4 crosswalk (OSDEV-3414), loaded
    from api/isic_taxonomy/data/os_hub_to_isic4_crosswalk.csv (Facility Type
    / Processing Type) and os_hub_sector_to_isic4_crosswalk.csv (Sector).

    A row names either a sector or a facility type, never both. An empty
    processing_type on a facility type row is the facility-type-only row. A
    row with no ISIC codes records a value that deliberately maps to
    nothing.
    '''

    sector = models.CharField(max_length=200, blank=True)
    facility_type = models.CharField(max_length=200, blank=True)
    processing_type = models.CharField(max_length=200, blank=True)
    isic_section = models.CharField(max_length=1, blank=True)
    isic_section_title = models.CharField(max_length=300, blank=True)
    isic_division = models.CharField(max_length=2, blank=True)
    isic_division_title = models.CharField(max_length=300, blank=True)
    isic_group = models.CharField(max_length=3, blank=True)
    isic_group_title = models.CharField(max_length=300, blank=True)
    isic_class = models.CharField(max_length=4, blank=True)
    isic_class_title = models.CharField(max_length=300, blank=True)
