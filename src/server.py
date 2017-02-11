# encoding: utf-8
"""Small localtcp/ip server to host connections from local client."""

import socket
import datetime


buffer_length = 1024
address = ('127.0.0.1', 5000)

responses = {
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed'),
    500: ('Internal Server Error'),
    505: ('HTTP Version Not Supported')
}


def response_ok():
    """Return a well formed HTTP 200 OK response."""
    response = 'HTTP/1.1 200 OK\r\n'
    response += 'Content-Type: text/plain\r\n'
    response += 'Date: ' + datetime.datetime.now().strftime('%a %b %Y %X PST') + '\r\n'
    return response


def response_error(err_code):
    """Return a well formed Error response."""
    response = 'HTTP/1.1 {0} {1}\r\n'
    response += 'Content-Type: text/plain\r\n'
    response += 'Date: ' + datetime.datetime.now().strftime('%a %b %Y %X PST') + '\r\n'
    return ''.join(response).format(err_code, responses[err_code][0])


def main():
    """Call server."""
    server()


def parse_request(message):
    """Validate that the request is well-formed if it is return the URI from the request."""
    requestline = message.rstrip('\r\n')
    print(requestline)
    request_split = requestline.split()
    print(request_split)
    command, path, version, host, host_name = request_split
    version_number = version.split('/', 1)[1]
    try:
        if command != 'GET':
            raise ValueError(405)
        elif 'HTTP/' not in version:
            raise ValueError(400)
        elif len(version_number) != 3 or version_number != '1.1':
                raise ValueError(505)
        if host != 'Host:' or host_name != address[0]:
            raise ValueError(400)
    except ValueError:
        raise
    return path


def build_error(string):
    """Build html error message."""
    html = """
    <!DOCTYPE html>
    <html>
        <body>
            <h1>{}</h1>
        </body>
    </html>
    """
    return html.format(string)


# def resolve_uri(uri):
#     """Take a URI parsed from a request.

#     It will return a body for a response with the type of
#     content contained in the body.
#     """


def handle_message(conn, buffer_length):
    """Handle the messages coming into the server."""
    conn.setblocking(1)
    message = []
    while True:
        part = conn.recv(buffer_length)
        message.append(part)
        print('Receiving message from client...')
        print('consuming: ', len(part))
        if len(part) < buffer_length or part[-2:] == b'\r\n':
            print('setting message to complete: ')
            break
        else:
            print('Hold on, there is more...Receiving...')
    print('parsing request...')

    full_message = b''.join(message)
    try:
        parse_request(full_message.decode('utf8'))
        print('Request OK')
        return response_ok().encode('utf8')
    except ValueError as e:
        return response_error(*e.args).encode('utf8')


def initialize_connection():
    """Set up a socket a connection and return socket object."""
    server = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM,
                           socket.IPPROTO_TCP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('entering server')
    server.bind(address)
    server.listen(1)
    print('listening on: ', address)
    return server


def server():
    """Start the server to listen and accept http requests."""
    server = initialize_connection()

    while True:
        try:
            conn, addr = server.accept()
            print('Received a connection by: ', addr)
            message = handle_message(conn, buffer_length)
        except KeyboardInterrupt:
            print('\n\nShutting Down Server...')
            try:
                conn.close()
            except UnboundLocalError:
                pass
            server.close()
            exit()
        print('Sending response... ')

        try:
            conn.sendall(message)
            print(message)
        except socket.error as se:
            print('Something went wrong when attempting to send to client:', se)
        print('Closing connection for: ', addr)
        print('Still listening...(Control + C to stop server)')
        conn.close()
    print('end: ', message)

if __name__ == '__main__':
    main()
