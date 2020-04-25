"""Testing server class"""

from server_v10.connection import Connection

# launching N clients for testing
#
# import os
# os.chdir("../client_v10")
# for _ in range(3):
#     os.startfile("cmd.exe")
# os.chdir("../server_v10")

print(f"SERVER LAUNCHED at address: {Connection.IP}:{Connection.PORT}")
my_server = Connection("server")
