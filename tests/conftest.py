import pytest
def pytest_addoption(parser):

    parser.addoption('--port'     ,action="store" ,default=8020)
    parser.addoption('--ip'       ,action="store" ,default="localhost")
    parser.addoption('--address'  ,action="store" ,default='')
    parser.addoption('--sleep'    ,action="store" ,default=1)
    parser.addoption('--headless' ,action='store_true',default=False)
