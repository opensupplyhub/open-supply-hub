from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Builds the partial indexes on the organization columns added by
    0269 without blocking writes to api_source, api_moderationevent and
    api_facilityclaim. Only rows that belong to an organization are
    indexed, so the indexes start empty. Concurrent builds cannot run
    inside a transaction, hence atomic = False.
    """

    atomic = False

    dependencies = [
        ('api', '0271_add_organization_level'),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="facilityclaim",
            index=models.Index(
                condition=models.Q(("organization__isnull", False)),
                fields=["organization"],
                name="api_facilityclaim_org_idx",
            ),
        ),
        AddIndexConcurrently(
            model_name="moderationevent",
            index=models.Index(
                condition=models.Q(("organization__isnull", False)),
                fields=["organization"],
                name="api_modevent_org_idx",
            ),
        ),
        AddIndexConcurrently(
            model_name="source",
            index=models.Index(
                condition=models.Q(("organization__isnull", False)),
                fields=["organization"],
                name="api_source_org_idx",
            ),
        ),
    ]
