'''
The vocabulary of claim quality warnings. Kept free of model and
service imports so serializers can import it too.
'''
# Maps each verdict returned by ClaimQualityService to the warning shown
# to the claimant when it is flagged, in the order they are shown. To
# add another AI-judgable check, add a field to ClaimQualityVerdicts and
# an entry here. The titles double as the vocabulary of the warning
# `type` values a write may report as dismissed.
WARNING_TITLES = {
    'name_quality': 'Name May Not Look Like a Facility Name',
    'address_quality': 'Address May Not Look Like a Facility Address',
    'address_country_mismatch': 'Address May Not Match Selected Country',
    'multiple_locations': 'Details May Describe Multiple Locations',
    'different_location': 'Details May Describe a Different Location',
}
