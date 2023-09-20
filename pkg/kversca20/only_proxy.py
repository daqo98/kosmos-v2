import logging
import os
import sys
import socket
import select
from threading import Timer, Thread
import time

from KVerSca20_operator import *

# Create and configure logger
logging.basicConfig(filename='logger.log', filemode='a', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG) #, datefmt='%m/%d/%Y %H:%M:%S %z')
logger = logging.getLogger("sidecar_proxy")
container_to_forward = os.environ['CONTAINER_TO_FORWARD'] #"http-metrics"
# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
BUFFERSIZE = 4096
DELAY = 0.0001
forward_to = ('127.0.0.1', getContainersPort(container_to_forward)) # Find port number of the service !!!!!!!!!!
PROXY_PORT = 80
TIME_SHORT = 30.0 # Timer to zeroimport logging
TIME_LONG = 90.0
HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
INTERNAL_PROXY_ADDR = ('127.0.0.1', PROXY_PORT)
# Get the local host name
myHostName = socket.gethostname()
logger.info(f"Name of the localhost is {myHostName}")
# Get the IP address of the local host
myIP = socket.gethostbyname(myHostName)
logger.info(f"IP address of the localhost is {myIP}")
EXTERNAL_PROXY_ADDR = (myIP,PROXY_PORT)
PROXY_LIST = [INTERNAL_PROXY_ADDR, EXTERNAL_PROXY_ADDR]

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            logger.error(e)
            return False

class TheServer:
    """
    Sidecar proxy server 

    Args:
        host: Address to which the server listens to
        port: Port to which the server listens to

    Returns:
        Instance of TheServer object
    """
    input_list = []
    channel = {}
    waiting_time_interval = 1 # in seconds
    separator = "____________________________________________________________________________________________________"

    def __init__(self, host, port):
        self.conn_orig = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)
        self.zero_state = ResourcesState(cpu_req="10m", cpu_lim="10m")
        self.fd_to_client_dict = {}


    def main_loop(self):
        """
        Flow logic of the proxy server. 
        Args: Self
        Returns: Nothing
        """
        self.input_list.append(self.server)
        self.create_and_start_timer(TIME_SHORT)
        while True:
            time.sleep(DELAY)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.conn_orig in inputready:
                if self.conn_orig == self.server:
                    self.on_accept() # Attempt to connect client
                    break
                try:
                    self.data = self.conn_orig.recv(BUFFERSIZE)
                except Exception as e:
                    logger.error("Error caused by socket.recv(BUFFERSIZE)")
                    logger.error(e)

                if len(self.data.decode()) == 0:
                    logger.debug("Empty buffer!")
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            logger.info(self.separator)
            logger.info(f"{clientaddr} has connected")
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
            self.fd_to_client_dict[clientsock.fileno()] = clientaddr
        else:
            logger.info("Can't establish connection with remote server.")
            logger.info(f"Closing connection with client side {clientaddr}")
            clientsock.close()

    def on_close(self):
        try:
            if self.conn_orig.fileno() in self.fd_to_client_dict:
                client_addr = self.conn_orig.getpeername()
                logger.info(f"{client_addr} has disconnected by CLIENT-PROXY socket")
            else:
                client_addr = self.channel[self.conn_orig].getpeername()
                logger.info(f"{client_addr} has disconnected by PROXY-APP socket")
        except:
            # Client-side disconnection
            if self.conn_orig.fileno() in self.fd_to_client_dict:
                client_addr = self.fd_to_client_dict[self.conn_orig.fileno()]
                logger.info(f"{client_addr} has disconnected by CLIENT-PROXY socket (getpeername() error)")
            # Server-side disconnection
            else:
                client_addr = self.fd_to_client_dict[self.channel[self.conn_orig].fileno()]
                logger.info(f"{client_addr} has disconnected by PROXY-APP socket (getpeername() error)")
        # Deleting entry from file descriptor to client dictionary
        # Client-side disconnection
        if self.conn_orig.fileno() in self.fd_to_client_dict:
            del self.fd_to_client_dict[self.conn_orig.fileno()]
        # Server-side disconnection
        else:
            del self.fd_to_client_dict[self.channel[self.conn_orig].fileno()]
        # remove objects from input_list
        self.input_list.remove(self.conn_orig)
        self.input_list.remove(self.channel[self.conn_orig])
        out = self.channel[self.conn_orig]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.conn_orig.close()
        # close the connection with remote server
        self.channel[self.conn_orig].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.conn_orig]
        logger.info(self.separator)

    def on_recv(self):
        data = self.data
        logger.info(data)   
        try:
            self.channel[self.conn_orig].send(data)
        except Exception as e:
            logger.error("Error caused by socket.send(data)")
            logger.error(e)
            self.on_close()

if __name__ == '__main__':
    server = TheServer('0.0.0.0', PROXY_PORT) # Socket of the Proxy server
    try:
        server.main_loop()
    except KeyboardInterrupt:
        logger.info("Ctrl C - Stopping server")
        sys.exit(1)