"""Testing server class"""

# local files
# DELETE "server." as a reference (it is there to run both client and server from one project directory)
from server.connection import Connection

print(f"SERVER LAUNCHED at address: {Connection.IP}:{Connection.PORT}")
my_server = Connection("server")
