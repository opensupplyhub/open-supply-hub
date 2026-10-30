"""Tests for the threshold preset helpers in upload_page: parsing --preset values and building their buttons."""
import os
import sys
import tempfile
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
                         [("6k best", 0.76, 0.30, None, None), ("a=b", 0.8, 0.5, None, None)])

    def test_group_and_tolerance(self):
        """A model and a tolerance can follow the pair: LABEL=AUTO/FLOOR/GROUP/TOLERANCE."""
        self.assertEqual(up.parse_presets(["6k, +1 sd=0.76/0.32/chal6k/sd"]), [("6k, +1 sd", 0.76, 0.32, "chal6k", "sd")])

    def test_bad_values_exit_with_a_message(self):
        """A missing slash, a non-number, a missing label or a number outside 0 to 1 all stop with a plain message."""
        for bad in ("nolabel", "x=0.8", "x=a/b", "=0.8/0.5", "x=1.5/0.5", "x=0.8/0.5/g/loose", "x=0.8/0.5/g/sd/extra"):
            with self.assertRaises(SystemExit):
                up.parse_presets([bad])


class PresetButtons(unittest.TestCase):
    """The HTML for the extra buttons."""

    def test_button_carries_the_numbers_the_page_reads(self):
        """data-a and data-f are the attributes the page's click handler reads, and the label is shown with the pair."""
        html = up.preset_buttons([("6k best", 0.76, 0.30, None, None)])
        self.assertIn('data-a="0.76" data-f="0.3"', html)
        self.assertIn("6k best (0.76 / 0.30)", html)

    def test_label_is_escaped(self):
        """A label with markup characters cannot break the page."""
        self.assertNotIn("<b>", up.preset_buttons([("<b>x</b>", 0.8, 0.5, None, None)]))

    def test_group_and_tolerance_become_attributes(self):
        """The page script reads data-g (the model) and data-tol (the tolerance) from the button."""
        html = up.preset_buttons([("6k", 0.76, 0.30, "chal6k", "worst")])
        self.assertIn('data-g="chal6k" data-tol="worst"', html)

    def test_no_presets_gives_nothing(self):
        """Without presets the page is exactly what it was."""
        self.assertEqual(up.preset_buttons([]), "")


class CompactEncoding(unittest.TestCase):
    """The packed format used by --compact."""

    def decode(self, text, lengths):
        """Decode a base64 string of little-endian uint16 values (x 10000) into per-upload lists, as the page script does."""
        import base64
        raw = base64.b64decode(text)
        out, k = [], 0
        for n in lengths:
            out.append([(raw[k + 2 * j] | (raw[k + 2 * j + 1] << 8)) / 10000 for j in range(n)])
            k += 2 * n
        return out

    def test_scores_round_trip_exactly(self):
        """Scores rounded to four places survive packing and unpacking unchanged, including 0 and 1."""
        rows = [[0.9744], [0.0, 1.0, 0.5], [], [0.0001, 0.9999]]
        self.assertEqual(self.decode(up.encode_scores(rows), [len(r) for r in rows]), rows)

    def test_ret_joins_the_strings(self):
        """The retrieval flags of every upload become one string, which the page splits again by candidate count."""
        self.assertEqual(up.encode_ret(["1", "01", "0"]), "1010")


class ParseStart(unittest.TestCase):
    """--start values."""

    def test_group_pair_and_tolerance(self):
        """GROUP=AUTO/FLOOR with an optional tolerance."""
        self.assertEqual(up.parse_start("chal6k=0.76/0.30/average"), ("chal6k", 0.76, 0.30, "average"))
        self.assertEqual(up.parse_start("chal6k=0.76/0.30"), ("chal6k", 0.76, 0.30, None))

    def test_bad_values_exit_with_a_message(self):
        """A missing group, a non-number, a number outside 0 to 1 or an unknown tolerance all stop with a plain message."""
        for bad in ("chal6k", "=0.8/0.5", "g=a/b", "g=1.5/0.5", "g=0.8/0.5/loose"):
            with self.assertRaises(SystemExit):
                up.parse_start(bad)


class LoadWeights(unittest.TestCase):
    """The production-volume CSV the weighting checkbox reads."""

    def write(self, text):
        """Write text to a temporary CSV and return its path."""
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        f.write(text)
        f.close()
        return f.name

    def test_codes_are_lowercased_and_counts_are_ints(self):
        """Country codes become lowercase, matching the page's country codes, and counts become whole numbers."""
        path = self.write("country,list_items\nCN,80388\nbr,76741\n")
        self.assertEqual(up.load_weights(path), {"cn": 80388, "br": 76741})

    def test_blank_and_non_numeric_rows_are_skipped(self):
        """A row with no country, or a count that is not a whole number, is left out instead of breaking the page."""
        path = self.write("country,n\n,5\nUS,many\nGB,18904\n")
        self.assertEqual(up.load_weights(path), {"gb": 18904})


class ParseWeightSpecs(unittest.TestCase):
    """--weights values."""

    def test_label_and_bare_path(self):
        """"LABEL=PATH" keeps its label; a bare path gets the default label."""
        self.assertEqual(up.parse_weight_specs(["last 4 months=v4.csv", "v.csv"], "volume"),
                         [("last 4 months", "v4.csv"), ("volume", "v.csv")])


class WeightControls(unittest.TestCase):
    """The controls for weighting the overall rows."""

    def test_no_weights_means_no_controls(self):
        """A page built without --weights looks exactly as before."""
        self.assertEqual(up.weight_controls({"weightSets": []}), "")

    def test_one_set_is_a_checkbox_that_names_it(self):
        """With one set, the checkbox says what the weights are and there is no menu."""
        html = up.weight_controls({"weightSets": [{"label": "list items since 2026-01-01", "weights": {"cn": 1}}]})
        self.assertIn('id="weighted"', html)
        self.assertIn("list items since 2026-01-01", html)
        self.assertNotIn('id="wset"', html)

    def test_two_sets_add_a_menu(self):
        """With more than one set, a menu lets the viewer choose the period, each option holding its label."""
        html = up.weight_controls({"weightSets": [{"label": "since Jan", "weights": {}}, {"label": "last 4 months", "weights": {}}]})
        self.assertIn('id="wset"', html)
        self.assertIn("last 4 months", html)


if __name__ == "__main__":
    unittest.main()
