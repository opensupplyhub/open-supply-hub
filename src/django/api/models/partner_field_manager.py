from django.db.models import Manager


class PartnerFieldManager(Manager):
    '''Custom manager for PartnerField that filters by active status.'''

    def get_queryset(self):
        '''Return only active partner fields by default.'''
        return super().get_queryset().filter(active=True)

    def get_all_including_inactive(self):
        '''Return all partner fields, including inactive ones.'''
        return super().get_queryset()
