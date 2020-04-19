"""A simple static website built with sockets"""

import os
import socket

IP = "192.168.88.239"  # 127.0.0.1, localhost
PORT = 1234
BUFF_SIZE = 2 ** 7
ENCODING = "UTF-8"

links = {
    "/": "pages/index.html",
    "/index.html": "pages/index.html",
    "/about.html": "pages/about.html",
    "/favicon.ico": "pages/favicon.ico",
    "/css/styles.css": "pages/css/styles.css",
    "/img/background.png": "pages/img/background.png",
    "/404.html": "pages/404.html",
    "/showroom.html": "pages/showroom.html"
}

content_type = {
    "/": "text/html",
    "/index.html": "text/html",
    "/styles.css": "text/css",
    "/favicon.ico": "image/png"}


def create_header(request):
    """Returns prepared header"""

    request = f"/{request}"
    header = "HTTP/1.1 200 OK\n" + f"content-type={content_type.get(request, 'text/html')}\n\n"
    header = header.encode("utf-8")
    return header


def get_request(client):
    """Gets full length request"""

    request = ""
    while True:

        request_chunk = client.recv(BUFF_SIZE).decode(ENCODING)

        if not request_chunk:
            break

        request += request_chunk

        if request[-4:] == "\r\n\r\n":
            break

    return request


def build_response(request):
    """Prepares an html page based on request"""

    req_page = request.split()[1]

    if req_page not in links:
        req_page = "/404.html"

    with open(links[req_page], "rb") as rf:
        body = rf.read()

    page = create_header(request) + body
    return page


def send_response(remote, response):
    """Properly sends the entire page"""

    resp_len = len(response)
    total_sent = 0
    while total_sent < resp_len:
        sent = remote.send(response[total_sent:])
        total_sent += sent


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as host_socket:
    host_socket.bind((IP, PORT))
    host_socket.listen(5)

    while True:
        print("Listening..")
        remote_socket, address = host_socket.accept()
        with remote_socket:
            print(f"Connection: {address}")
            req = get_request(remote_socket)
            resp = build_response(req)
            send_response(remote_socket, resp)

            # remote_socket.shutdown(socket.SHUT_RDWR)
            # remote_socket.close()
