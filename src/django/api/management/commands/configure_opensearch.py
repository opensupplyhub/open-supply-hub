from django.core.management.base import BaseCommand
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from api.models.settings import Settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Configure OpenSearch settings for the application."

    def handle(self, *args, **options):
        """
        Configures OpenSearch settings for the application.
        This command sets up the necessary configurations for OpenSearch
        to ensure proper functionality and integration with the application.
        """
        opensearch = OpenSearchServiceConnection()

        logger.info(
            "Setting up OpenSearch cluster settings for Machine Learning!")
        settings_res = opensearch.client.cluster.put_settings(
            body={
                "persistent": {
                    "plugins.ml_commons.only_run_on_ml_node": "false",
                    "plugins.ml_commons.model_access_control_enabled": "true",
                    "plugins.ml_commons.native_memory_threshold": "99",
                }
            },
        )

        if not settings_res["acknowledged"]:
            logger.error("Failed to configure cluster settings!")
            raise RuntimeError("Failed to configure cluster settings!")

        logger.info("Cluster settings configured successfully!")

        model_group_id = Settings.get(
            description="Model group ID for OpenSearch embedding generation model.",
            name=Settings.Name.OS_SENTENCE_TRANSFORMER_GROUP_ID,
        )

        if not model_group_id.value:
            logger.info(
                "Creating model group for OpenSearch embedding generation model.")
            model_reg_res = opensearch.client.plugins.ml.register_model_group(
                body={
                    "name": "NLP_Models",
                    "description": "A model group for NLP models.",
                },
            )
            model_group_id.value = model_reg_res["model_group_id"]
            model_group_id.save()
            logger.info(
                "Model group with ID '%s' created successfully!",
                model_reg_res["model_group_id"],
            )
        else:
            logger.info("Model group ID already exists.")

        logger.info(model_group_id.value)
