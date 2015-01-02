import unittest
import sys
import os
from mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from serial_messanger import SerialMessanger


class SerialMessangerTest(unittest.TestCase):
    def call_back(*args):
        pass

    def test_register_id_must_be_between_0_and_255(self):
        mock_connection = Mock()
        test_serial_messanger = SerialMessanger(mock_connection)
        with self.assertRaises(Exception):
            test_serial_messanger.register(-1, self.call_back, type(123))
        with self.assertRaises(Exception):
            test_serial_messanger.register(256, self.call_back, type(123))

        test_serial_messanger.register(1, self.call_back, type(123))


if __name__ == '__main__':
    unittest.main()
