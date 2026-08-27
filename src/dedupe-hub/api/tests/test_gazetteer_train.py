import unittest
from unittest.mock import MagicMock, mock_open, patch

from app.matching.matcher.gazeteer.gazetteer_train import gazetteer_train


class TestGazetteerTrain(unittest.TestCase):
    @patch(
        'app.matching.matcher.gazeteer.gazetteer_train.open',
        new_callable=mock_open,
        read_data='{"match": [], "distinct": []}',
    )
    @patch('app.matching.matcher.gazeteer.gazetteer_train.Gazetteer')
    def test_train_disables_index_predicates(self, gazetteer_cls, _mock_open):
        gazetteer = gazetteer_cls.return_value
        messy = {'1': {'country': 'us', 'name': 'acme', 'address': '1 main st'}}
        canonical = {
            'OS1': {'country': 'us', 'name': 'acme', 'address': '1 main st'}
        }

        result = gazetteer_train(messy, canonical, should_index=True)

        self.assertIs(result, gazetteer)
        gazetteer.train.assert_called_once_with(index_predicates=False)
        gazetteer.index.assert_called_once_with(canonical)
        gazetteer.cleanupTraining.assert_called_once()

    @patch('app.matching.matcher.gazeteer.gazetteer_train.StaticGazetteer')
    def test_model_settings_skip_train(self, static_gazetteer_cls):
        gazetteer = static_gazetteer_cls.return_value
        model_settings = MagicMock()
        canonical = {
            'OS1': {'country': 'us', 'name': 'acme', 'address': '1 main st'}
        }

        result = gazetteer_train(
            {}, canonical, model_settings=model_settings, should_index=True
        )

        self.assertIs(result, gazetteer)
        gazetteer.train.assert_not_called()
        gazetteer.index.assert_called_once_with(canonical)
