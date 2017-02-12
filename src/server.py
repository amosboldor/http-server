# encoding: utf-8
"""Small localtcp/ip server to host connections from local client."""

import socket
import datetime
import os
from mimetypes import MimeTypes


buffer_length = 1024
address = ('127.0.0.1', 5000)

responses = {
    400: ('Bad Request', 'Bad request syntax or unsupported method'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed', 'Specified method is invalid for this resource.'),
    500: ('Internal Server Error', 'Server got itself in trouble'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.')
}


def response_ok(body, content_type):
    """Return a well formed HTTP 200 OK response."""
    response = b'HTTP/1.1 200 OK\r\n'
    response += b'Date: ' + str(datetime.datetime.now().strftime('%a %b %Y %X PST')).encode() + b'\r\n'
    response += b'Connection: close\r\n'
    response += b'Content-Type: ' + content_type + b'\r\n'
    response += b'Content-Length: ' + str(len(body)).encode() + b'\r\n\r\n'
    response += body + b'\r\n'
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
    request_split = message.split()
    try:
        if len(request_split) > 5:
            raise ValueError(405)
        elif request_split[0] != 'GET':
            raise ValueError(405)
        elif 'HTTP/' not in request_split[2]:
            raise ValueError(400)
        elif '1.1' not in request_split[2]:
            raise ValueError(505)
        if request_split[3] != 'Host:' or request_split[4] != address[0]:
            raise ValueError(400)
    except ValueError:
        pass
    return request_split[1]


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


def folder_contents_html(files, folders):
    """Given files and folders generate html."""
    html = """
    <!DOCTYPE html>
    <html>
        <body>
            {}
        </body>
    </html>
    """
    files_and_folders = ''
    for folder in folders:
        files_and_folders += '<h4>' + folder + '</h4>'
    for file in files:
        files_and_folders += '<h4>' + file + '</h4>'
    return html.format(files_and_folders)


def get_path(path):
    """Search for file or directory and returns path."""
    for root, dirs, files in os.walk(os.path.abspath('webroot')):
        for directory in dirs:
            if directory == path:
                return os.path.join(root, directory)
        for file in files:
            if file == path:
                return os.path.join(root, file)


def resolve_uri(uri):
    """Take a URI parsed from a request.

    It will return a body for a response with the type of
    content contained in the body.
    """
    path = get_path(uri.split('/')[-1]) if uri != '/' else 'webroot'
    if path and os.path.isfile(path):
        with open(path, mode='rb') as file:
            file_content = file.read()
            mime = MimeTypes()
            content_type = mime.guess_type(path)[0]
            print(len(file_content))
            return file_content, str(content_type).encode()
    elif path and os.path.isdir(path):
        contents = os.listdir(path)
        files = []
        folders = []
        for x in contents:
            if os.path.isfile(os.path.abspath(x)):
                files.append(x)
            else:
                folders.append(x)
        return str(folder_contents_html(files, folders)).encode(), b'text/html'
    else:
        raise ValueError(404)


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
        uri = parse_request(full_message.decode('utf8'))
        body, content_type = resolve_uri(uri)
        return response_ok(body, content_type)
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
