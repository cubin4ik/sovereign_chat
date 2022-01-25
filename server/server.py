"""Testing server class"""

# local files
# DELETE "server." as a reference (it is there to run both client and server from one project directory)
from server.connection import Connection

if __name__ == '__main__':
    print(f"LAUNCHING SERVER at address: {Connection.IP}:{Connection.PORT}")
    Connection('server')
