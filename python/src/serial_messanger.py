import struct
import threading
import time

''' TODO:
1. Logging 
2. Sending Messages
3. Length Specifier
4. CheckSum
'''

'''Tool for serial communication alling for registration and call back of methods based on input data
Usage:
'''


class SerialMessanger(threading.Thread):
    '''Initialize the class with a started connection matching the pyserialAPI (http://pyserial.sourceforge.net/pyserial_api.html)
    Notes:
        You will need to manage the starting and stopping of this connection outside of this class'''
    def __init__(self,
                 connection,
                 header='HEAD',
                 footer='FOOT',
                 handshake="c",
                 handshake_timeout_sec=3):
        threading.Thread.__init__(self)
        self.connection = connection
        if self.connection.timeout is None:
            self.connection.timeout = 0.1
        self.header = header
        self.footer = footer
        self.handshake = handshake
        self.handshake_timeout_sec = handshake_timeout_sec
        self._read_chuck_size = 10

        self._running = False
        self._connection_failure = None
        self._registered_messages = {}

    '''Registers a handler and arg types for a specific message id.
    message_id - Message ids should be an integer between 0 and 255 (inclusive)
    callback   - Method taking the types as parameters
    types      - A list of ordered c-types (struct-like) corrosponding to the callback parameters'''
    def register(self, message_id, callback, types):
        self._is_valid_id(message_id)
        self._is_valid_types(types)
        self._registered_messages[str(message_id)] = (types, callback)

    '''Shutdowns thread'''
    def close(self):
        self._running = False
        while self.is_alive():
            time.sleep(0.1)

    '''Blocking start until handshake is complete'''
    def start(self):
        super(SerialMessanger, self).start()
        while not self._running and self._connection_failure is None:
            time.sleep(0.1)
        if not self._running:
            raise Exception(self._connection_failure)

    '''sends a tuple message with data as ctypes'''
    def send_message(self, messageid, data_tuple, types):
        self._is_valid_id(messageid)
        self._is_valid_types(types)
        packed_data = struct.pack('!' + types, *data_tuple)

    def _is_valid_id(self, message_id):
        if message_id < 0 or message_id > 255:
            raise Exception('Message Id must be a integer between 0 and 255 (inclusive)')

    def _is_valid_types(self, types):
        for special in ['<', '>', '@', '=', '!']:
            assert(not special in types)
        try:
            struct.calcsize(types)
        except Exception as ex:
            raise ex

    def _do_handshake(self):
        if self.handshake:
            timeout = time.time() + self.handshake_timeout_sec
            handshake = self.header + self.handshake + self.footer
            self.connection.write(handshake)
            recieved = ''
            while not handshake in recieved and time.time() < timeout:
                read = self.connection.read(10)
                recieved += read
            if not handshake in recieved:
                self._connection_failure = "Handshake Timed Out"
                raise Exception("Handshake Timed Out")

    def _process_data(self, data):
        message_id = str(struct.unpack('!h', data[:2])[0])
        message_length = struct.unpack('!h', data[2:4])[0]

        if message_id in self._registered_messages:
            types, callback = self._registered_messages[message_id]
            fmt = '!' + types
            try:
                data_tuple = struct.unpack(fmt, data[4:4+message_length])
            except Exception as ex:
                print(data)
                raise ex
            callback(*data_tuple)

    @property
    def _minimum_message_length(self):
        return len(self.header) + 2 + 2 + len(self.footer)

    @property
    def _preamble_length(self):
        return len(self.header) + 2 + 2

    def run(self):
        self.connection.flushInput()
        self.connection.flushOutput()
        try:
            self._do_handshake()
            self._running = True
            raw_data = ''
            while(self._running):
                raw_data += self.connection.read(self._read_chuck_size)
                header_index = raw_data.find(self.header)
                if len(raw_data[header_index:]) >= self._minimum_message_length:
                    length = struct.unpack('!h', raw_data[header_index + len(self.header) + 2:][:2])[0]
                    footer_index = header_index + self._preamble_length + length
                    if len(raw_data[header_index:]) >= footer_index:
                        if self.footer == raw_data[footer_index:footer_index + len(self.footer)]:
                            self._process_data(raw_data[header_index + len(self.header):footer_index])
                            raw_data = raw_data[footer_index + len(self.footer):]

        except Exception as ex:
            print(ex)
        finally:
            self._running = False
