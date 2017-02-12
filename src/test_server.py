"""Tests for server.py."""
import pytest


BAD_REQUESTS = [
    ["GET /index.html HTTP/1.1\r\nHost: me", "HTTP/1.1 404 Not Found"],
    ["GET /index.html HTTP/1.1\r\nDate: 12/12/12\r\n\r\n", "HTTP/1.1 404 Not Found"],
    ["GET /index.html HTTP/1.0\r\nHost: \r\n\r\n", "HTTP/1.1 505 HTTP Version Not Supported"],
    ["POST www.stuff.com HTTP/1.1\r\nHost: me\r\n\r\n", "HTTP/1.1 405 Method Not Allowed"]
]


@pytest.mark.parametrize("req,resp", BAD_REQUESTS)
def test_bad_request_errors(req, resp):
    """Test specific request errors."""
    from client import client
    assert client(req).split('\r\n')[0] == resp


def test_client_valid():
    """Test client with valid request."""
    from client import client
    body = 'This is a very simple text file.\nJust to show that we can serve it up.\nIt is three lines long.\n'
    req = "GET sample.txt HTTP/1.1\r\nHost: me\r\n\r\n"
    assert body in client(req)
