from django.test import TestCase


class ProcessingTestCase(TestCase):
    def get_first_status(self, item, action):
        return next(
            r for r in item.processing_results if r["action"] == action
        )

    def assert_status(self, item, action):
        self.assertIsNotNone(self.get_first_status(item, action))
