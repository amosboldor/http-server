# encoding: utf-8
"""Small localtcp/ip server to host connections from local client."""

import socket
import datetime
import os
from mimetypes import MimeTypes

walk_dir = os.getcwd()
if walk_dir.split('/')[-1] != 'src':  # code to make tox work
    walk_dir += '/src'
walk_dir += '/webroot'


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
    response += 'Date: ' + datetime.datetime.now().strftime('%a %b %Y %X PST') + '\r\n'
    return ''.join(response).format(err_code, responses[err_code][0])


def parse_request(message):  # pragma: no cover
    """Validate that the request is well-formed if it is return the URI from the request."""
    request_split = message.split()
    # import pdb; pdb.set_trace()
    if request_split[0] != 'GET':
        raise ValueError(405)
    elif 'HTTP/' not in request_split[2]:
        raise ValueError(400)
    elif '1.1' not in request_split[2]:
        raise ValueError(505)
    return request_split[1]


def folder_contents_html(folder_path, files, folders):
    """Given files and folders generate html."""
    html = "<!DOCTYPE html><html><body>{}</body></html>"
    atag = '<a href="{}">{}</a>'
    files_and_folders = ''
    for folder in folders:
        files_and_folders += '<h4>' + atag.format(folder_path + '/' + folder, folder) + '</h4>'
    for file in files:
        files_and_folders += '<h4>' + atag.format(folder_path + '/' + file, file) + '</h4>'
    return html.format(files_and_folders)


def get_path(path):
    """Search for file or directory and returns path."""
    for root, dirs, files in os.walk(walk_dir):
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
    path = get_path(uri.split('/')[-1]) if uri != '/' else walk_dir
    # import pdb; pdb.set_trace()
    if path and os.path.isfile(path):
        with open(path, mode='rb') as file:
            file_content = file.read()
            mime = MimeTypes()
            content_type = mime.guess_type(path)[0]
            return file_content, str(content_type).encode()
    elif path and os.path.isdir(path):
        contents = os.listdir(path)
        files = []
        folders = []
        folder_path = path.split('webroot')[-1]
        for x in contents:
            if os.path.isfile(os.path.abspath(x)):
                files.append(x)
            else:
                folders.append(x)
        return str(folder_contents_html(folder_path, files, folders)).encode(), b'text/html'
    else:
        raise ValueError(404)


def handle_message(conn, buffer_length):
    """Handle the messages coming into the server."""
    conn.setblocking(1)
    message = []
    while True:
        part = conn.recv(buffer_length)
        message.append(part)
        print('Receiving message from client...\n')
        if len(part) < buffer_length or part[-2:] == b'\r\n':
            break
        else:
            print('Hold on, there is more...Receiving...')
    print('parsing request...\n')

    full_message = b''.join(message)
    try:
        uri = parse_request(full_message.decode('utf8'))
        body, content_type = resolve_uri(uri)
        message = response_ok(body, content_type)
    except ValueError as e:
        message = response_error(*e.args).encode('utf8')
    print('Sending Response...\n')
    conn.sendall(message)
    conn.close()


def initialize_connection():
    """Set up a socket a connection and return socket object."""
    server = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM,
                           socket.IPPROTO_TCP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    server.listen(1)
    print('\n', 'Server running on http://127.0.0.1:{}/'.format(address[1]), '\n')
    return server


def server():
    """Start the server to listen and accept http requests."""
    server = initialize_connection()

    while True:
        try:
            conn, addr = server.accept()
            print('Received a connection from: ', addr)
            handle_message(conn, buffer_length)
        except KeyboardInterrupt:
            print('\n\nShutting Down Server...')
            server.close()
            exit()
        except socket.error as se:
            print('Something went wrong when attempting to send to client:', se)
        print('Closing connection from: ', addr)
        print('Still listening...(Control + C to stop server)')


if __name__ == '__main__':
    server()
