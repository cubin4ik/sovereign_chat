"""Testing server class"""

import os
from server_v10.connection import Connection

os.chdir("../client_v10")
for _ in range(1):
    os.startfile("cmd.exe")
os.chdir("../server_v10")

print(f"SERVER LAUNCHED")
my_server = Connection("server")
