"""Tests for the threshold preset helpers in upload_page: parsing --preset values and building their buttons."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
import upload_page as up  # noqa: E402


class ParsePresets(unittest.TestCase):
    """--preset LABEL=AUTO/FLOOR values."""

    def test_label_auto_floor(self):
        """The auto bar comes first and the label may itself contain an equals sign."""
        self.assertEqual(up.parse_presets(["6k best=0.76/0.30", "a=b=0.8/0.5"]),
                         [("6k best", 0.76, 0.30), ("a=b", 0.8, 0.5)])

    def test_bad_values_exit_with_a_message(self):
        """A missing slash, a non-number, a missing label or a number outside 0 to 1 all stop with a plain message."""
        for bad in ("nolabel", "x=0.8", "x=a/b", "=0.8/0.5", "x=1.5/0.5"):
            with self.assertRaises(SystemExit):
                up.parse_presets([bad])


class PresetButtons(unittest.TestCase):
    """The HTML for the extra buttons."""

    def test_button_carries_the_numbers_the_page_reads(self):
        """data-a and data-f are the attributes the page's click handler reads, and the label is shown with the pair."""
        html = up.preset_buttons([("6k best", 0.76, 0.30)])
        self.assertIn('data-a="0.76" data-f="0.3"', html)
        self.assertIn("6k best (0.76 / 0.30)", html)

    def test_label_is_escaped(self):
        """A label with markup characters cannot break the page."""
        self.assertNotIn("<b>", up.preset_buttons([("<b>x</b>", 0.8, 0.5)]))

    def test_no_presets_gives_nothing(self):
        """Without presets the page is exactly what it was."""
        self.assertEqual(up.preset_buttons([]), "")


if __name__ == "__main__":
    unittest.main()
