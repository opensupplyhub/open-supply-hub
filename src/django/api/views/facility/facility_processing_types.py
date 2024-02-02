from rest_framework.decorators import (
  api_view,
  throttle_classes,
)
from rest_framework.response import Response
from ...facility_type_processing_type import FACILITY_PROCESSING_TYPES_VALUES


@api_view(['GET'])
@throttle_classes([])
def facility_processing_types(_):
    """
    Returns an array of objects with facilityType set to the name of a facility
    type and processingTypes set to an array of processing types associated
    with that facility type.

    ## Sample Response

        [{
            "facilityType": "Final Product Assembly",
            "processingTypes": [
              "Assembly",
              "Cut & Sew",
              "Cutting",
              "Embellishment",
              "Embroidery",
              ...
            ]
          },
          ...
         ]

    """
    return Response(FACILITY_PROCESSING_TYPES_VALUES)
