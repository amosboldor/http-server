# HTTP Server

This is an implementation of a simple socket server.

## Contains:
    - Modules:
        - client.py
        - server.py
        - concurrency.py
    - Tests:
        - test_server.py

## Use:
####Clone Down:
```bash
git clone https://github.com/amosboldor/http-server.git
```
####Move in to repo folder: 
```bash 
cd http-server
```
####Create enviroment:
```bash
python3 -m venv ENV
```
####Source in to enviroment:
```bash
source ENV/bin/activate
```
####Install: 
```bash
python setup.py install
```
`python src/server.py` or `python src/concurrency.py`to run the server.
You can then open your browser localhost and request files from the webroot.
Alternatively you can open the client in another terminal and type `python3 client <request>`, request being a valid HTTP GET request.


## Coverage:

###Python 3

```
================================== test session starts ====================================
platform linux2 -- Python 2.7.12+, pytest-3.0.6, py-1.4.32, pluggy-0.4.0
rootdir: /home/x/codefellows/401/http-server, inifile: 
plugins: cov-2.4.0
collected 35 items 

src/test_server.py ...................................

---------- coverage: platform linux2, python 2.7.12-final-0 ----------
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src/client.py           32      4    88%   45-48
src/concurrency.py       5      5     0%   2-8
src/server.py          107     44    59%   100, 110-133, 138-145, 150-164, 168
src/test_server.py      49      0   100%
--------------------------------------------------
TOTAL                  193     53    73%


================================= 35 passed in 0.11 seconds =================================
```

###Python 2
```
==================================== test session starts ====================================
platform linux -- Python 3.5.2+, pytest-3.0.6, py-1.4.32, pluggy-0.4.0
rootdir: /home/x/codefellows/401/http-server, inifile: 
plugins: cov-2.4.0
collected 35 items 

src/test_server.py ...................................

----------- coverage: platform linux, python 3.5.2-final-0 -----------
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src/client.py           32      4    88%   45-48
src/concurrency.py       5      5     0%   2-8
src/server.py          107     44    59%   100, 110-133, 138-145, 150-164, 168
src/test_server.py      49      0   100%
--------------------------------------------------
TOTAL                  193     53    73%


================================ 35 passed in 0.14 seconds ==================================
```

## Authors:
Ford Fowler and Maelle Vance