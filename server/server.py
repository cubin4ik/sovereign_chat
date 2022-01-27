"""Testing server class"""

# standard libraries
import logging

# local files
from server.connection import Connection
# DELETE "server." as a reference (it is there to run both client and server from one project directory)

logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(asctime)s - %(message)s')

if __name__ == '__main__':
    logging.info(f"LAUNCHING SERVER at address: {Connection.IP}:{Connection.PORT}")
    Connection('server')
