"""Testing client class"""

from web.connection import Connection

my_client = Connection()
resp = my_client.send_req("Hello world! This is a test message of my super sophisticated new program. Enjoy!")
print(resp)
