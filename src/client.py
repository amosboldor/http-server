# encoding: utf-8
"""Local TCP/IP client to send/receive messages to local server."""

import socket
import sys


buffer_length = 8


def initialize_connection():
    """Set up a socket a connection and return socket object."""
    infos = socket.getaddrinfo('127.0.0.1', 5000)
    stream_info = [i for i in infos if i[1] == socket.SOCK_STREAM][0]
    client = socket.socket(*stream_info[:3])
    client.connect(stream_info[-1])
    return client


def client(message):
    """Send a http request to the local server and return http response."""
    client = initialize_connection()

    print('sending the following message:',
          message, 'to server at: ',
          socket.gethostbyname('127.0.0.1'))
    if sys.version[0] == '3':
        client.sendall(message.encode('utf8') + b'\r\n')
    else:
        client.sendall(message + b'\r\n')

    server_message = []
    while True:
        part = client.recv(buffer_length)
        if part:
            server_message.append(part)
            print('Receiving message from server...')
            print(part)
        if len(part) < buffer_length or part[-2:] == b'\r\n':
            break
        else:
            print('Hold on, there is more...Receiving...')
    client.close()
    print('\n')
    return b''.join(server_message).decode('utf8')


if __name__ == '__main__':
    message = sys.argv[1]
    if "\\r\\n" in message:
                message = message.replace("\\r\\n", "\r\n")
    print(client(message))
