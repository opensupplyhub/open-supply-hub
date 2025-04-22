from django.core.management.base import BaseCommand
from api.services.opensearch.opensearch import OpenSearchServiceConnection
from api.models.settings import Settings
import logging
import time

logger = logging.getLogger(__name__)

INGESTION_PIPELINE_ID = "nlp_index_pipeline"
SEARCH_PIPELINE_ID = "nlp_search_pipeline"


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
            model_group_id.update(value=model_reg_res["model_group_id"])
            logger.info(
                "Model group with ID '%s' created successfully!",
                model_reg_res["model_group_id"],
            )
        else:
            logger.info("Model group with ID '%s' already exists.",
                        model_group_id.value)

        model_id = Settings.get(
            name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_ID,
            description="Model ID for OpenSearch embedding generation model.",
        )

        if not model_id.value:
            logger.info(
                "Creating model for OpenSearch embedding generation model.")
            model_name = Settings.get(
                name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_NAME,
                description="Model name for OpenSearch embedding generation model.",
                value="huggingface/sentence-transformers/all-MiniLM-L6-v2",
            )
            model_reg_res = opensearch.client.plugins.ml.register_model(
                body={
                    "name": model_name.value,
                    "version": "1.0.1",
                    "model_group_id": model_group_id.value,
                    "model_format": "TORCH_SCRIPT",
                },
            )
            logger.info(
                "Model registration task with ID '%s' created successfully!",
                model_reg_res["task_id"],
            )

            while True:
                task_res = opensearch.client.plugins.ml.get_task(
                    task_id=model_reg_res["task_id"],
                )

                if task_res["state"] == "COMPLETED":
                    model_id.update(value=task_res["model_id"])
                    logger.info(
                        "Model with ID '%s' created successfully!",
                        task_res["model_id"],
                    )
                    break

                if task_res["state"] == "FAILED":
                    raise RuntimeError(
                        "Model creation failed!",
                    )

                logger.info(
                    "Waiting for model creation to complete! Task state: '%s'",
                    task_res["state"],
                )

                time.sleep(2)
        else:
            logger.info("Model with ID '%s' already exists.",
                        model_id.value)

        search_models_res = opensearch.client.plugins.ml.search_models(
            body={
                "query": {
                    "ids": {
                        "values": [
                            model_id.value,
                        ],
                    },
                },
            },
        )

        model = search_models_res["hits"]["hits"][0]["_source"]

        if model["model_state"] != "DEPLOYED":
            logger.info(
                "Deploying model with ID '%s'.",
                model_id.value,
            )
            deploy_res = opensearch.client.plugins.ml.deploy_model(
                model_id=model_id.value,
            )

            while True:
                task_res = opensearch.client.plugins.ml.get_task(
                    task_id=deploy_res["task_id"],
                )

                if task_res["state"] == "COMPLETED":
                    logger.info("Model with ID '%s' deployed successfully!",
                                model_id.value)
                    break

                if task_res["state"] == "FAILED":
                    logger.error(
                        "Model deployment with ID '%s' failed! Task state: '%s'",
                        model_id.value,
                        task_res["state"],
                    )
                    raise RuntimeError("Model deployment failed!")

                logger.info(
                    "Waiting for model deployment with ID '%s'! Task state: '%s'",
                    model_id.value,
                    task_res["state"],
                )

                time.sleep(2)

        ingestion_pipeline_id = Settings.get(
            name=Settings.Name.OS_INGESTION_PIPELINE_ID,
            description="Ingestion pipeline for OpenSearch embedding generation model.",
            value=INGESTION_PIPELINE_ID,
        )

        ingestion_pipeline_res = opensearch.client.ingest.put_pipeline(
            id=ingestion_pipeline_id.value,
            body={
                "description": "An NLP ingestion pipeline!",
                "processors": [
                    {
                        "text_embedding": {
                            "model_id": model_id.value,
                            "field_map": {
                                "name": "name_embedding",
                                "address": "address_embedding",
                            },
                        },
                    },
                ],
            },
        )

        if not ingestion_pipeline_res["acknowledged"]:
            logger.error(
                "Failed to configure ingestion pipeline, update not acknowledged!")
            raise RuntimeError("Failed to configure ingestion pipeline!")
        else:
            logger.info(
                "Ingestion pipeline with ID '%s' updated successfully!",
                ingestion_pipeline_id.value,
            )

        search_pipeline_id = Settings.get(
            name=Settings.Name.OS_SEARCH_PIPELINE_ID,
            description="Search pipeline for OpenSearch hybrid search.",
            value=SEARCH_PIPELINE_ID,
        )

        search_pipeline_res = opensearch.client.search_pipeline.put(
            id=search_pipeline_id.value,
            body={
                "description": "Post processor for hybrid search.",
                "phase_results_processors": [
                    {
                        "normalization-processor": {
                            "normalization": {
                                "technique": "min_max"
                            },
                            "combination": {
                                "technique": "arithmetic_mean"
                            }
                        }
                    }
                ]
            }
        )

        if not search_pipeline_res["acknowledged"]:
            logger.error(
                "Failed to configure search pipeline, update not acknowledged!")
            raise RuntimeError("Failed to configure search pipeline!")
        else:
            logger.info(
                "Search pipeline with ID '%s' updated successfully!",
                search_pipeline_id.value,
            )

        logger.info("OpenSearch settings configured successfully!")
