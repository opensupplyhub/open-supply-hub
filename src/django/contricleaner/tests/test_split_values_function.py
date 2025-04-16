from django.test import TestCase

from contricleaner.lib.helpers.split_values import split_values


class SplitValuesFunctionTest(TestCase):
    def test_string_split(self):
        # Test splitting a string
        result = split_values("Apparel,Toys,Food", ",")
        self.assertCountEqual(result, ["Apparel", "Toys", "Food"])

    def test_list_split(self):
        # Test splitting a list of strings
        result = split_values(["Apparel,Toys", "Food,Coal"], ",")
        self.assertCountEqual(result, ["Apparel", "Toys", "Food", "Coal"])

    def test_set_split(self):
        # Test splitting a set of strings
        result = split_values({"Apparel,Toys", "Food,Coal"}, ",")
        self.assertCountEqual(result, ["Apparel", "Toys", "Food", "Coal"])

    def test_mixed_type_split(self):
        # Test splitting a mix of string, list, and set
        result = split_values(
            ["Apparel", "Toys,Coal", ["Books, Energy"], {"Food|Gas"}],
            r", |,|\|",
        )
        self.assertCountEqual(
            result,
            [
                "Apparel",
                "Toys",
                "Coal",
                "Books",
                "Energy",
                "Food",
                "Gas",
            ],
        )
