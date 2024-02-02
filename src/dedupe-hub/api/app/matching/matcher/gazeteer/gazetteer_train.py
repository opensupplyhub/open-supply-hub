import os
import logging
from datetime import datetime
from typing import BinaryIO, Union
from typing import Dict

from dedupe import Gazetteer, StaticGazetteer
from app.utils.constants import BASE_DIR

logger = logging.getLogger(__name__)


def gazetteer_train(
    messy: Dict[str, Dict[str, str]],
    canonical: Dict[str, Dict[str, str]],
    model_settings: BinaryIO or None = None,
    should_index: bool = False
) -> Union[Gazetteer, StaticGazetteer]:
    """
    Train and return a dedupe.Gazetteer using the specified messy and canonical
    dictionaries. The messy and canonical objects should have the same
    structure:
      - The key is a unique ID
      - The value is another dictionary of field:value pairs. This dictionary
        must contain at least 'country', 'name', and 'address' keys.

    Reads a training.json file containing positive and negative matches.
    """
    if model_settings:
        gazetteer = StaticGazetteer(model_settings)
    else:
        fields = [
            {'field': 'country', 'type': 'Exact'},
            {'field': 'name', 'type': 'String'},
            {'field': 'address', 'type': 'String'},
        ]

        gazetteer = Gazetteer(fields)
        gazetteer.sample(messy, canonical, 15000)
        training_file = os.path.join(BASE_DIR, 'data',
                                     'training.json')
        with open(training_file) as tf:
            gazetteer.readTraining(tf)
        gazetteer.train()
        gazetteer.cleanupTraining()

    if should_index:
        index_start = datetime.now()
        logger.info('Indexing started')
        gazetteer.index(canonical)
        index_duration = datetime.now() - index_start
        logger.info(f'Indexing finished ({index_duration})')
        logger.info('Cleanup training')

    return gazetteer
