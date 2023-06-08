import pytest
def pytest_addoption(parser):
    usage='''Usage:
    serve.py [-p|--port=<port_nb>] [-d|--debug] [-h|--help]

    OPTIONS
    -------
        - port : port number (default 8020)
        - q    : headless mode (default False)
        - h    : show this help
    '''
    # parser = argparse.ArgumentParser()
    parser.addoption('--headless' ,action='store_true',default=False)
    parser.addoption('--port'     ,action="store" ,default=8020)
    parser.addoption('--sleep'    ,action="store" ,default=1)
    # print(parser)
    # args = parser.parse_args()

    # print(args)
