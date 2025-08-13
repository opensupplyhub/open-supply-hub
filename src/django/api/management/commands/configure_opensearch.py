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

        self._configure_cluster_settings(opensearch)

        model_group_id = self._ensure_model_group(opensearch)
        model_id = self._ensure_model(opensearch, model_group_id)

        model_id = self._deploy_model_if_needed(opensearch, model_id)
        self._configure_ingestion_pipeline(opensearch, model_id)
        self._configure_search_pipeline(opensearch)

        logger.info("OpenSearch settings configured successfully!")

    def _configure_cluster_settings(self, opensearch) -> None:
        logger.info(
            "Setting up OpenSearch cluster settings for Machine Learning!"
        )
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

    def _ensure_model_group(self, opensearch) -> str:
        model_group_id_setting = Settings.get(
            description=(
                "Model group ID for OpenSearch embedding generation model."
            ),
            name=Settings.Name.OS_SENTENCE_TRANSFORMER_GROUP_ID,
        )

        if model_group_id_setting.value:
            logger.info(
                "Model group with ID '%s' already exists.",
                model_group_id_setting.value,
            )
            return model_group_id_setting.value

        logger.info(
            "Creating model group for OpenSearch embedding generation model."
        )
        model_reg_res = opensearch.client.plugins.ml.register_model_group(
            body={
                "name": "NLP_Models",
                "description": "A model group for NLP models.",
            },
        )
        model_group_id_setting.update(value=model_reg_res["model_group_id"])
        logger.info(
            "Model group with ID '%s' created successfully!",
            model_reg_res["model_group_id"],
        )
        return model_reg_res["model_group_id"]

    def _ensure_model(self, opensearch, model_group_id: str) -> str:
        model_id_setting = Settings.get(
            name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_ID,
            description=(
                "Model ID for OpenSearch embedding generation model."
            ),
        )

        if model_id_setting.value:
            logger.info(
                "Model with ID '%s' already exists.",
                model_id_setting.value,
            )
            return model_id_setting.value

        logger.info(
            "Creating model for OpenSearch embedding generation model."
        )
        model_name = Settings.get(
            name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_NAME,
            description=(
                "Model name for OpenSearch embedding generation model."
            ),
            value="huggingface/sentence-transformers/all-MiniLM-L6-v2",
        )
        model_reg_res = opensearch.client.plugins.ml.register_model(
            body={
                "name": model_name.value,
                "version": "1.0.1",
                "model_group_id": model_group_id,
                "model_format": "TORCH_SCRIPT",
            },
        )
        logger.info(
            "Model registration task '%s' created!",
            model_reg_res["task_id"],
        )

        task_res = self._wait_for_task_completion(
            opensearch,
            model_reg_res["task_id"],
            context_description="model creation to complete",
            failure_message="Model creation failed!",
        )
        model_id_setting.update(value=task_res["model_id"])
        logger.info(
            "Model with ID '%s' created successfully!",
            task_res["model_id"],
        )
        return task_res["model_id"]

    def _deploy_model_if_needed(self, opensearch, model_id: str) -> str:
        search_models_res = opensearch.client.plugins.ml.search_models(
            body={
                "query": {
                    "ids": {
                        "values": [
                            model_id,
                        ],
                    },
                },
            },
        )
        hits = search_models_res.get("hits", {}).get("hits", [])

        # If the configured model_id is not found in OpenSearch,
        # re-register and update the model_id_setting.
        if not hits:
            logger.warning(
                "Model with ID '%s' not found. Re-registering a new model.",
                model_id,
            )

            # Retrieve settings objects to update values
            model_group_id_setting = Settings.get(
                description=(
                    "Model group ID for OpenSearch embedding generation model."
                ),
                name=Settings.Name.OS_SENTENCE_TRANSFORMER_GROUP_ID,
            )
            model_id_setting = Settings.get(
                name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_ID,
                description=(
                    "Model ID for OpenSearch embedding generation model."
                ),
            )
            model_name = Settings.get(
                name=Settings.Name.OS_SENTENCE_TRANSFORMER_MODEL_NAME,
                description=(
                    "Model name for OpenSearch embedding generation model."
                ),
                value="huggingface/sentence-transformers/all-MiniLM-L6-v2",
            )

            # Do not set value to None to avoid NOT NULL constraint;
            # _ensure_model will register and persist the new model id
            # into the setting.

            # Register a new model directly and persist its ID
            model_reg_res = opensearch.client.plugins.ml.register_model(
                body={
                    "name": model_name.value,
                    "version": "1.0.1",
                    "model_group_id": model_group_id_setting.value,
                    "model_format": "TORCH_SCRIPT",
                },
            )
            logger.info(
                "Model registration task with ID '%s' created successfully!",
                model_reg_res["task_id"],
            )
            try:
                task_res = self._wait_for_task_completion(
                    opensearch,
                    model_reg_res["task_id"],
                    context_description="model creation to complete (retry)",
                    failure_message=(
                        "Model creation failed after retry!"
                    ),
                )
            except RuntimeError as e:
                # If model group is missing in OpenSearch,
                # create a new one and retry once.
                if "get model group" in str(e).lower():
                    logger.warning(
                        (
                            "Model group missing. "
                            "Creating a new group and retrying."
                        )
                    )
                    new_group_res = (
                        opensearch.client.plugins.ml
                        .register_model_group(
                            body={
                                "name": "NLP_Models",
                                "description": (
                                    "A model group for NLP models."
                                ),
                            },
                        )
                    )
                    model_group_id_setting.update(
                        value=new_group_res["model_group_id"]
                    )
                    # Retry registration with the new group id
                    model_reg_res = (
                        opensearch.client.plugins.ml
                        .register_model(
                            body={
                                "name": model_name.value,
                                "version": "1.0.1",
                                "model_group_id": (
                                    new_group_res["model_group_id"]
                                ),
                                "model_format": "TORCH_SCRIPT",
                            },
                        )
                    )
                    logger.info(
                        (
                            "Model registration task with ID '%s' created "
                            "successfully (retry)!"
                        ),
                        model_reg_res["task_id"],
                    )
                    task_res = self._wait_for_task_completion(
                        opensearch,
                        model_reg_res["task_id"],
                        context_description=(
                            "model creation to complete (retry)"
                        ),
                        failure_message=(
                            "Model creation failed after retry!"
                        ),
                    )
                else:
                    raise
            model_id = task_res["model_id"]
            model_id_setting.update(value=model_id)

            # Search again for the newly created model
            search_models_res = opensearch.client.plugins.ml.search_models(
                body={
                    "query": {
                        "ids": {
                            "values": [model_id],
                        },
                    },
                },
            )
            hits = search_models_res.get("hits", {}).get("hits", [])

            if not hits:
                logger.error(
                    (
                        "Failed to find newly registered model '%s' in "
                        "OpenSearch."
                    ),
                    model_id,
                )
                raise RuntimeError(
                    "Model registration lookup failed; cannot proceed."
                )

        model = hits[0]["_source"]

        if model["model_state"] == "DEPLOYED":
            logger.info("Model with ID '%s' already deployed.", model_id)
            return model_id

        logger.info(
            "Deploying model with ID '%s'.",
            model_id,
        )
        deploy_res = opensearch.client.plugins.ml.deploy_model(
            model_id=model_id,
        )

        self._wait_for_task_completion(
            opensearch,
            deploy_res["task_id"],
            context_description=f"model deployment with ID '{model_id}'",
            failure_message="Model deployment failed!",
        )
        logger.info("Model with ID '%s' deployed successfully!", model_id)
        return model_id

    def _configure_ingestion_pipeline(self, opensearch, model_id: str) -> None:
        ingestion_pipeline_id = Settings.get(
            name=Settings.Name.OS_INGESTION_PIPELINE_ID,
            description=(
                "Ingestion pipeline for OpenSearch embedding generation model."
            ),
            value=INGESTION_PIPELINE_ID,
        )

        ingestion_pipeline_res = opensearch.client.ingest.put_pipeline(
            id=ingestion_pipeline_id.value,
            body={
                "description": "An NLP ingestion pipeline!",
                "processors": [
                    {
                        "text_embedding": {
                            "model_id": model_id,
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
                "Failed to configure ingestion pipeline, update not "
                "acknowledged!"
            )
            raise RuntimeError("Failed to configure ingestion pipeline!")

        logger.info(
            "Ingestion pipeline with ID '%s' updated successfully!",
            ingestion_pipeline_id.value,
        )

    def _configure_search_pipeline(self, opensearch) -> None:
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
                "Failed to configure search pipeline, update not acknowledged!"
            )
            raise RuntimeError("Failed to configure search pipeline!")

        logger.info(
            "Search pipeline with ID '%s' updated successfully!",
            search_pipeline_id.value,
        )

    def _wait_for_task_completion(
        self,
        opensearch,
        task_id: str,
        context_description: str,
        failure_message: str,
    ) -> dict:
        while True:
            task_res = opensearch.client.plugins.ml.get_task(
                task_id=task_id,
            )

            if task_res["state"] == "COMPLETED":
                return task_res

            if task_res["state"] == "FAILED":
                logger.error(
                    "%s Task state: '%s'",
                    failure_message,
                    task_res["state"],
                )
                error_detail = task_res.get("error")
                raise RuntimeError(f"{failure_message} Error: {error_detail}")

            logger.info(
                "Waiting for %s! Task state: '%s'",
                context_description,
                task_res["state"],
            )

            time.sleep(2)
