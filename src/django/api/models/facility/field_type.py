from django.db.models import IntegerChoices


class FieldType(IntegerChoices):
    RAW = 0
    COMPUTE = 1
