import unittest
import sys
import os
import time
from mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from serial_messanger import SerialMessanger


class SerialMessangerTest(unittest.TestCase):
    def call_back(self, *args):
        self.call_back_args = args

    def setUp(self):
        self.time_to_wait_async = 0.2
        self.call_back_args = None
        self.test_serial_messanger = None
        self.mock_connection = MagicMock()
        self.test_serial_messanger = SerialMessanger(self.mock_connection, handshake=None)

    def tearDown(self):
        if self.test_serial_messanger:
            if self.test_serial_messanger.is_alive():
                self.test_serial_messanger.close()
                self.test_serial_messanger.join(1)

    def test_starts_and_stops(self):
        self.mock_connection.read.return_value = ''
        self.test_serial_messanger.start()
        self.assertEquals(True, self.test_serial_messanger.is_alive())
        self.test_serial_messanger.close()
        self.assertEquals(False, self.test_serial_messanger.is_alive())
        self.test_serial_messanger.join(1)

    def test_start_flushes_connection(self):
        self.mock_connection.read.return_value = ''
        self.test_serial_messanger.start()
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)
        self.mock_connection.flushInput.assert_called_with()
        self.mock_connection.flushOutput.assert_called_with()

    def test_start_should_transmit_handshake_if_provided_and_wait_for_a_response(self):
        expected_header = 'aaa'
        expected_footer = 'ccc'
        expected_handshake = 'hello'
        send_bytes = expected_header + expected_handshake + expected_footer
        return_bytes = list(send_bytes)

        def side_effect(self):
            if return_bytes:
                return return_bytes.pop(0)
            else:
                return ''

        self.mock_connection.read.side_effect = side_effect
        self.test_serial_messanger = SerialMessanger(self.mock_connection, header=expected_header, footer=expected_footer, handshake=expected_handshake)
        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)
        self.mock_connection.write.assert_called_with(send_bytes)

    def test_never_recieves_handshake(self):
        expected_header = 'aaa'
        expected_footer = 'ccc'
        expected_handshake = 'hello'
        self.mock_connection.read.return_value = 'z'
        self.test_serial_messanger = SerialMessanger(self.mock_connection, header=expected_header, footer=expected_footer, handshake=expected_handshake, handshake_timeout_sec=0.3)
        with self.assertRaises(Exception):
            self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.assertFalse(self.test_serial_messanger.is_alive())

    def test_register_id_must_be_between_0_and_255(self):
        with self.assertRaises(Exception):
            self.test_serial_messanger.register(-1, self.call_back, 'h')
        with self.assertRaises(Exception):
            self.test_serial_messanger.register(256, self.call_back, 'h')

        self.test_serial_messanger.register(1, self.call_back, 'h')

    def test_register_types_must_be_struct_compatible(self):
        with self.assertRaises(Exception):
            self.test_serial_messanger.register(1, self.call_back, 'a')
        with self.assertRaises(Exception):
            self.test_serial_messanger.register(1, self.call_back, type(123))
        self.test_serial_messanger.register(1, self.call_back, 'b')

    def test_register_types_should_not_accept_special_characters(self):
        for character in ['<h', '>h', '@h', '=h', '!h']:
            with self.assertRaises(Exception):
                self.test_serial_messanger.register(1, self.call_back, character)

    def test_when_data_for_registered_message_is_recieved_call_back_is_issued(self):
        self.test_serial_messanger.register(1, self.call_back, 'l')
        self.mock_connection.read.return_value = 'HEAD\x00\x01\x00\x04\x00\x00\x00\x17FOOT'

        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)

        self.assertEquals((23,), self.call_back_args)

    def test_when_data_for_registered_message_of_complex_type_is_recieved_call_back_is_issued(self):
        self.test_serial_messanger.register(1, self.call_back, 'hh')
        self.mock_connection.read.return_value = 'HEAD\x00\x01\x00\x04\x00\x00\x00\x17FOOT'

        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)

        self.assertEquals((0, 23), self.call_back_args)

    def test_when_data_for_registered_message_and_wrong_length_is_recieved_doesnt_call(self):
        self.test_serial_messanger.register(1, self.call_back, 'hh')
        self.mock_connection.read.return_value = 'HEAD\x00\x01\x00\x00\x17FOOT'

        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)

        self.assertEquals(None, self.call_back_args)

    def test_when_data_for_registered_message_contains_footer(self):
        self.test_serial_messanger.register(1, self.call_back, 'l')
        self.mock_connection.read.return_value = 'HEAD\x00\x01\x00\x04FOOTFOOT'

        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)

        self.assertEquals((1179602772,), self.call_back_args)

    def test_when_data_for_registered_message_contains_header(self):
        self.test_serial_messanger.register(1, self.call_back, 'l')
        self.mock_connection.read.return_value = 'HEAD\x00\x01\x00\x04HEADFOOT'

        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)

        self.assertEquals((1212498244,), self.call_back_args)

    def test_when_data_preceeds_header(self):
        self.test_serial_messanger.register(1, self.call_back, 'l')
        self.mock_connection.read.return_value = '\x34HEAD\x00\x01\x00\x04\x00\x00\x00\x17FOOT'

        self.test_serial_messanger.start()
        time.sleep(self.time_to_wait_async)
        self.test_serial_messanger.close()
        self.test_serial_messanger.join(1)

        self.assertEquals((23,), self.call_back_args)

    # TODO JT 2015-01-06 - Come back to this
    # def test_when_data_containing_header_preceeds_header(self):
    #     self.test_serial_messanger.register(1, self.call_back, 'l')
    #     self.mock_connection.read.return_value = 'HEAD\x34HEAD\x00\x01\x00\x04\x00\x00\x00\x17FOOT'
    #     self.test_serial_messanger.start()
    #     time.sleep(self.time_to_wait_async)
    #     self.test_serial_messanger.close()
    #     self.test_serial_messanger.join(1)

    #     self.assertEquals((23,), self.call_back_args)

    def test_send_message_should_raise_exception_if_message_id_invalid(self):
        with self.assertRaises(Exception):
            self.test_serial_messanger.send_message('a', (123,), 'h')
        with self.assertRaises(Exception):
            self.test_serial_messanger.send_message(-1, (123,), 'h')
        with self.assertRaises(Exception):
            self.test_serial_messanger.send_message(256, (123,), 'h')

    def test_send_message_should_raise_exception_if_types_invalid(self):
        for character in ['<h', '>h', '@h', '=h', '!h']:
            with self.assertRaises(Exception):
                self.test_serial_messanger.send_message(1, (123,), character)
        with self.assertRaises(Exception):
            self.test_serial_messanger.send_message(1, (123,), 'r')

    def test_send_message_should_raise_exception_if_data_unmatched_types(self):
        with self.assertRaises(Exception):
            self.test_serial_messanger.send_message(1, ('asdf',), 'c')

    def test_send_message_should_write_message_to_serial(self):
        expected_packet = 'HEAD\x00\x01\x00\x04\x00\x00\x00\x17FOOT'

        self.test_serial_messanger.start()
        self.test_serial_messanger.send_message(1, (23,), 'l')
        self.test_serial_messanger.close()

        self.mock_connection.write.assert_called_with(expected_packet)

    def test_send_message_should_write_complex_message_to_serial(self):
        expected_packet = 'HEAD\x00\x01\x00\x04\x00\x17\x00\x17FOOT'

        self.test_serial_messanger.start()
        self.test_serial_messanger.send_message(1, (23, 23), 'hh')
        self.test_serial_messanger.close()

        self.mock_connection.write.assert_called_with(expected_packet)

    def test_send_messages_should_write_complex_message_to_serial_many_times(self):
        expected_packet1 = 'HEAD\x00\x01\x00\x04\x00\x17\x00\x17FOOT'
        expected_packet2 = 'HEAD\x00\x02\x00\x04\x00\x00\x00\x17FOOT'

        self.test_serial_messanger.start()
        self.test_serial_messanger.send_message(1, (23, 23), 'hh')
        self.test_serial_messanger.send_message(2, (23,), 'l')
        self.test_serial_messanger.close()

        self.mock_connection.write.calls[0][0][1](expected_packet1)
        self.mock_connection.write.calls[0][0][1](expected_packet2)

    def test_send_message_should_raise_exception_if_not_strated(self):
        with self.assertRaises(Exception):
            self.test_serial_messanger.send_message(1, (23,), 'l')

if __name__ == '__main__':
    unittest.main()
