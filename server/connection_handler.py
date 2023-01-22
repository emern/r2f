import socket
import threading
import queue
from enum import Enum

DEFAULT_PORT = 12000

class ThreadMsg(Enum):
    SHUT_DOWN = 0

"""
Generic thread handler object for handling new requests from many devices
"""
class ThreadHandler (threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
    def run(self):
        handle_connection_run(conn=self.conn, addr=self.addr)

"""
Generic connection handler object for assigning incoming connections to threads
"""
class ConnectionHandler (threading.Thread):
    def __init__(self, port, q):
        threading.Thread.__init__(self)
        self.port = port
        self.shutdown = q
    def run(self):
        connection_handler_run(self.shutdown, self.port)

"""
Connection manager wrapper for starting and stopping conneciton management
"""
class ConectionManagementObject:
    def __init__(self):
        self.msg_queue = queue.Queue()
        self.running = False
        self.port = DEFAULT_PORT
        self.connection_handler = ConnectionHandler(self.port, self.msg_queue)

    def start_connection_handler(self):
        # first check if handler is already running
        if (self.running == False):
            try:
                # create and start the connection handler
                connection_handler = ConnectionHandler(DEFAULT_PORT, self.msg_queue)
                connection_handler.start()
                self.running = True
            except:
                print("failed to start connection handler")
        else:
            print("Server connection handler already running!")

    """
    End the connection handler and stop accepting new connections
    """
    def end_connection_handler(self):
        print("disabling server connection handler")
        self.msg_queue.put(ThreadMsg.SHUT_DOWN)
        self.running = False


"""
Run the exception handler
"""
def connection_handler_run(shutdown, port=DEFAULT_PORT):

    print("starting server connection handler")
    all_connections = []
    # create the socket, bind to port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        # accept new connections
        while 1:
            # handle any new connections
            s.listen()
            s.setblocking(False)
            try :
                # try and read message from queue
                if (shutdown.get(False) == ThreadMsg.SHUT_DOWN):
                    # close incoming connection first
                    for t in all_connections:
                        t.join()
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    return
            except:
                # after processing any messages, then try and process incoming connections
                try:
                    conn, addr = s.accept()
                    newHandler = ThreadHandler(conn, addr)
                    newHandler.start()
                    all_connections.append(newHandler)
                except:
                    pass

    print("failed to start server host socket at port " + str(port))

"""
Handle connections
"""
def handle_connection_run(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            # just send data back for now
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
        conn.close()

con_man = ConectionManagementObject()

def start_connection_handler():
    con_man.start_connection_handler()

def end_connection_handler():
    con_man.end_connection_handler()

if __name__ == '__main__':
    None
