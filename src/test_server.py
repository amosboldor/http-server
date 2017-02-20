"""Tests for server.py."""
import pytest
import os
from client import client
from server import (
    parse_request,
    resolve_uri,
    folder_contents_html,
    get_path,
    response_ok,
    response_error
)

walk_dir = os.getcwd()
if walk_dir.split()[-1] != 'src':  # code to make tox work
    walk_dir += '/src'
walk_dir += '/webroot'


BAD_REQUESTS = [
    ["GET /index.html HTTP/1.1\r\nHost: me", "HTTP/1.1 404 Not Found"],
    ["GET /index.html HTTP/1.1\r\nDate: 12/12/12\r\n\r\n", "HTTP/1.1 404 Not Found"],
    ["GET /index.html HTTP/1.0\r\nHost: \r\n\r\n", "HTTP/1.1 505 HTTP Version Not Supported"],
    ["POST www.stuff.com HTTP/1.1\r\nHost: me\r\n\r\n", "HTTP/1.1 405 Method Not Allowed"]
]

REQUESTS_VALUE_ERROR = [
    b"POST www.stuff.com HTTP/1.1\r\nHost: bobdole\r\n\r\n",
    b"GET HTTP/1.1\r\nHost: bobdole\r\n\r\n",
    b"GET HTTP/1.1\r\nHost: bobdole",
    b"GET HTTP/1.1\r\nDate: 12\r\n\r\n",
    b"GET HTTP/1.1\r\nHost: \r\n\r\n",
    b"GET HTTP/1.1\r\n\r\nHost: bobdole\r\n\r\n",
    b"GET HTTP/1.1\r\nHost: \r\n\r\n\r\n",
    b"GET HTTP/1.1 Host: bobdole\r\n\r\n",
]

TYPES = [
    ["/images/Sample_Scene_Balls.jpg", b"image/jpeg"],
    ["/images/sample_1.png", b"image/png"],
    ["/sample.txt", b"text/plain"],
    ["/make_time.py", b"text/x-python"],
    ["/a_web_page.html", b"text/html"]
]

FILES_AND_FOLDERS = [
    ["Sample_Scene_Balls.jpg", "/images/Sample_Scene_Balls.jpg"],
    ["sample_1.png", "/images/sample_1.png"],
    ["sample.txt", '/sample.txt'],
    ["make_time.py", '/make_time.py'],
    ["a_web_page.html", '/a_web_page.html'],
    ["images", '/images']
]

ERRORS = [
    [404, "404 Not Found"],
    [405, "405 Method Not Allowed"],
    [400, "400 Bad Request"],
    [505, "505 HTTP Version Not Supported"],
    [500, "500 Internal Server Error"]
]


def test_folder_contents_html():
    """Test the generating html function with proper a tags."""
    html = folder_contents_html('/bobdole', ['slim.py'], ['pics'])
    assert '/bobdole/slim.py' in html
    assert '/bobdole/pics' in html


@pytest.mark.parametrize("file_name, file_path", FILES_AND_FOLDERS)
def test_get_path(file_name, file_path):
    """Test that get_path gets and returns file content and type."""
    assert get_path(file_name) == walk_dir + file_path


def test_response_ok_content_length():
    """Test content-length header."""
    headers = response_ok(b"bob dole", b'text/plain').split(b'\r\n\r\n')[0]
    assert headers.split(b'\r\n')[4] == b'Content-Length: 8'


def test_parse_request_ok():
    """Test parse_request with valid request."""
    req = "GET www.bobdole.com HTTP/1.1\r\nHost: hell\r\n\r\n"
    assert parse_request(req) == 'www.bobdole.com'


@pytest.mark.parametrize("request", REQUESTS_VALUE_ERROR)
def test_parse_request_value_error(request):
    """Test parse_request with invalid request."""
    with pytest.raises(ValueError):
        parse_request(request)


@pytest.mark.parametrize("error_code, error_msg", ERRORS)
def test_response_error_message(error_code, error_msg):
    """Test server response contains the right error message."""
    assert error_msg in response_error(error_code)


def test_resolve_uri_raises_err():
    """Test resolve_uri will raise the correct error if file not found."""
    with pytest.raises(ValueError, message=404):
        resolve_uri("bobdol")


@pytest.mark.parametrize("file_path, file_type", TYPES)
def test_resolve_uri_find_type(file_path, file_type):
    """Test resolve_uri will return the correct type."""
    assert resolve_uri(file_path)[1] == file_type


def test_resolve_uri_folder():
    """Test resolve_uri with folder path."""
    web_root_content = [
        b'images',
        b'make_time.py',
        b'._sample.txt',
        b'._images',
        b'a_web_page.html',
        b'._a_web_page.html',
        b'._make_time.py',
        b'sample.txt'
    ]
    html = resolve_uri('/')
    assert html[1] == b'text/html'
    for content in web_root_content:
        assert content in html[0]


@pytest.mark.parametrize("req,resp", BAD_REQUESTS)
def test_bad_request_errors(req, resp):
    """Test specific request errors."""
    assert client(req).split('\r\n')[0] == resp


def test_client_valid():
    """Test client with valid request."""
    body = 'This is a very simple text file.\nJust to show that we can serve it up.\nIt is three lines long.\n'
    req = "GET sample.txt HTTP/1.1\r\nHost: me\r\n\r\n"
    assert body in client(req)


def test_client_no_request():
    """Test client with no request."""
    assert '400' in client('')
