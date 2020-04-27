"""Testing server class"""

from server.connection import Connection

# launching N clients for testing
#
# import os
# os.chdir("../client")
# for _ in range(3):
#     os.startfile("cmd.exe")
# os.chdir("../server")

print(f"SERVER LAUNCHED at address: {Connection.IP}:{Connection.PORT}")
my_server = Connection("server")
