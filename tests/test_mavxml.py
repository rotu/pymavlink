#!/usr/bin/env python
"""
Module to test MAVXML
"""

from __future__ import print_function
import unittest

import importlib_resources as resources

from pymavlink.generator.mavparse import MAVXML
from pymavlink.generator.mavparse import MAVParseError

class MAVXMLTest(unittest.TestCase):
    """
    Class to test MAVXML
    """

    def test_fields_number(self):
        """Test that a message can have at most 64 fields"""
        test_filepath = resources.files(__name__) / "64-fields.xml"

        xml = MAVXML(test_filepath)
        count = len(xml.message[0].fields)
        self.assertEqual(count, 64)

        test_filepath = resources.files(__name__) / "65-fields.xml"

        with self.assertRaises(MAVParseError):
            _ = MAVXML(test_filepath)


    def test_wire_protocol_version(self):
        """Test that an unknown MAVLink wire protocol version raises an exception"""
        with self.assertRaises(MAVParseError):
            _ = MAVXML(filename="", wire_protocol_version=42)


if __name__ == '__main__':
    unittest.main()
