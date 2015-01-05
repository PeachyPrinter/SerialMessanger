import struct
import threading
import time


'''Tool for serial communication alling for registration and call back of methods based on input data
Usage:
'''


class SerialMessanger(threading.Thread):
    '''Initialize the class with a started connection matching the pyserialAPI (http://pyserial.sourceforge.net/pyserial_api.html)

    Notes: 
        You will need to manage the starting and stopping of this connection outside of this class'''
    def __init__(self,
                 connection,
                 header="a",
                 footer="b",
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

        self._running = False
        self._connection_failure = None

    '''Registers a handler and arg types for a specific message id.
    message_id - Message ids should be an integer between 0 and 255 (inclusive)
    callback   - Method taking the types as parameters
    types      - A list of ordered types corrosponding to the callback parameters'''
    def register(self, message_id, callback, types):
        self._is_valid_id(message_id)

    '''Shutdowns thread'''
    def close(self):
        self._running = False
        while self.is_alive():
            time.sleep(0.1)

    def start(self):
        super(SerialMessanger, self).start()
        while not self._running and self._connection_failure is None:
            time.sleep(0.1)
        if not self._running:
            raise Exception(self._connection_failure)

    def _is_valid_id(self, message_id):
        if message_id < 0 or message_id > 255:
            raise Exception('Message Id must be a integer between 0 and 255 (inclusive)')

    def _do_handshake(self):
        if self.handshake:
            timeout = time.time() + self.handshake_timeout_sec
            handshake = self.header + self.handshake + self.footer
            self.connection.write(handshake)
            recieved = ''
            while not handshake in recieved and time.time() < timeout:
                read = self.connection.read(1)
                recieved += read
            if not handshake in recieved:
                self._connection_failure = "Handshake Timed Out"
                raise Exception("Handshake Timed Out")

    def run(self):
        self.connection.flushInput()
        self.connection.flushOutput()
        try:
            self._do_handshake()
            self._running = True
            while(self._running):
                pass
        except Exception:
            pass
        finally:
            self._running = False
