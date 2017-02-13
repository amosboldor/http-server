"""Concurrency for our server.py module."""
from gevent.server import StreamServer
from gevent.monkey import patch_all
import sys
from server import handle_message


buffer_length = 1024


def start_server(port=5000):  # pragma: no cover
    """Start the stream server."""
    patch_all()
    stream_server = StreamServer(('127.0.0.1', port), connection)
    print('Server running on http://127.0.0.1:{}/'.format(port))
    try:
        stream_server.serve_forever()
    except KeyboardInterrupt:
        stream_server.close()
        print('Server closed')


def connection(socket, address):  # pragma: no cover
    """Handle new connections to stream server."""
    print('New connection from {}:{}'.format(address[0], address[1]))
    handle_message(socket, buffer_length)


if __name__ == '__main__':  # pragma: no cover
    try:
        start_server(sys.argv[1])
    except IndexError:
        start_server()
