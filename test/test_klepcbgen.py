import unittest

from kle_pcbgen import KLEPCBGenerator
from kle_pcbgen.klepcbgenmod import unit_width_to_available_footprint


class PCBGeneratorUnitTest(unittest.TestCase):
    def setUp(self):
        self.gen = KLEPCBGenerator(infile="abcd", outname="abcd")

    def test_unit_width(self):
        """Test unit width"""
        self.assertEqual(unit_width_to_available_footprint(1.0), "1.00")
        self.assertEqual(unit_width_to_available_footprint(1.3), "1.25")
        self.assertEqual(unit_width_to_available_footprint(1.5), "1.50")
        self.assertEqual(unit_width_to_available_footprint(1.8), "1.75")
        self.assertEqual(unit_width_to_available_footprint(2.1), "2.00")
        self.assertEqual(unit_width_to_available_footprint(2.4), "2.25")
        self.assertEqual(unit_width_to_available_footprint(5.0), "2.75")
        self.assertEqual(unit_width_to_available_footprint(9.0), "6.25")
