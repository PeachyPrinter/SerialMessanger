import sys
import serial
import time

from serial_messanger import SerialMessanger


class ExampleApp(object):
    def __init__(self, port):
        self.port = port

    def call_back(self, data):
        print('Recieved Data: %s' % data)

    def run(self):
        self.connection = serial.Serial(self.port)
        try:
            self.messanger = SerialMessanger(self.connection)
            self.messanger.register(1, self.call_back, 'l')
            self.messanger.start()
            for data in range(1, 10):
                self.messanger.send_message(1, (data,), 'l')
                print("Sent Data: %s" % data)
                time.sleep(1)
            self.messanger.close()
        finally:
            self.connection.close()
        self.running = False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Provide port as first arguement')
        exit(666)
    port = sys.argv[1]
    app = ExampleApp(port)

    app.run()
