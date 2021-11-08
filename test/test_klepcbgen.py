import unittest
from unittest.mock import patch, mock_open

from kle_pcbgen import KLEPCBGenerator
from kle_pcbgen.models import Key


class PCBGeneratorUnitTest(unittest.TestCase):
    def setUp(self):
        self.gen = KLEPCBGenerator(infile="abcd", outname="abcd")
        self.single_key = '[ [ { "a": 7 }, "" ] ]'

    def test_read_kle_json(self):
        """
        Read KLE json
        """
        with patch("builtins.open", mock_open(read_data=self.single_key)) as mock_file:
            self.gen.read_kle_json()
        assert self.gen.keyboard[0] == Key(
            x_unit=0.5,
            y_unit=0.5,
            width=1,
            height=1,
            number=0,
            legend="",
            rotation=0,
            diodenetnum=0,
            colnetnum=0,
            rownetnum=0,
        )
