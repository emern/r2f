import socket
import threading
import queue
from enum import Enum
import json
import tile_manager

DEFAULT_PORT = 12000

class ThreadMsg(Enum):
    SHUT_DOWN = 0

class ClientMsgCode(Enum):
    RESTAURANT_SEARCH_BY_NAME = 0,
    RESTAURANT_RECOMMENDATION_UPDATE = 1,
    RESTAURANT_GET_TOP_NEARBY = 2

"""
Generic thread handler object for handling new requests from many devices
"""
class ThreadHandler (threading.Thread):
    def __init__(self, conn, addr, tile_manager):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.tm = tile_manager
    def run(self):
        handle_connection_run(conn=self.conn, addr=self.addr, tile_manager=self.tm)

"""
Generic connection handler object for assigning incoming connections to threads
"""
class ConnectionHandler (threading.Thread):
    def __init__(self, port, q, tm):
        threading.Thread.__init__(self)
        self.port = port
        self.shutdown = q
        self.tm = tm
    def run(self):
        connection_handler_run(self.shutdown, self.tm, self.port)

"""
Connection manager wrapper for starting and stopping conneciton management
"""
class ConectionManagementObject:
    def __init__(self):
        self.msg_queue = queue.Queue()
        self.running = False
        self.port = DEFAULT_PORT
        self.tm = tile_manager.TileManager(tile_manager.API_KEY_FILE, tile_manager.TILE_DATABASE, tile_manager.RESTAURANT_DATABASE)
        self.connection_handler = ConnectionHandler(self.port, self.msg_queue, self.tm)

    def start_connection_handler(self):
        # first check if handler is already running
        if (self.running == False):
            try:
                # create and start the connection handler
                self.connection_handler = ConnectionHandler(self.port, self.msg_queue, self.tm)
                self.connection_handler.start()
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
def connection_handler_run(shutdown, tm, port=DEFAULT_PORT):

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
                    newHandler = ThreadHandler(conn, addr, tm)
                    newHandler.start()
                    all_connections.append(newHandler)
                except:
                    pass

    print("failed to start server host socket at port " + str(port))

"""
JSON encoder for handling Restaurant JSON type
"""
class RestaurantEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, tile_manager.Restaurant):
            return o.toJSON()
        return RestaurantEncoder(self, o)

"""
Handle connections
"""
def handle_connection_run(conn, addr, tile_manager):
    with conn:
        print(f"Connected by {addr}")
        data = conn.recv(1024)
        try:
            outgoing = ""
            # parse json
            incomming = json.loads(data)
            if (incomming["cmd"] == 0):
                # restaurant query function
                search_resp_data = tile_manager.search_for_restaurants_by_name(incomming["name"])
                out = {"restaurants" : search_resp_data, "response" : "OK"}
                outgoing = json.dumps(out, cls=RestaurantEncoder, sort_keys=True)
            elif (incomming["cmd"] == 1):
                tile_manager.update_restaurant_recommends_by_placeid(incomming["placeid"])
                out = {"response" : "OK"}
                outgoing = json.dumps(out)
            elif (incomming["cmd"] == 2):
                resp_data = tile_manager.get_top_results_in_radius(incomming["lat"], incomming["long"], incomming["num"], incomming["radius"])
                out = {"restaurants" : resp_data, "response" : "OK"}
                outgoing = json.dumps(out, cls=RestaurantEncoder, sort_keys=True)
        except:
            # operation failed
            outgoing = json.dumps({"response" : "ERROR"})
        conn.sendall(outgoing.encode("utf-8"))
    conn.close()

con_man = ConectionManagementObject()

def start_connection_handler():
    con_man.start_connection_handler()

def end_connection_handler():
    con_man.end_connection_handler()

if __name__ == '__main__':
    None
