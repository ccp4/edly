import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def pytest_addoption(parser):

    ##
    parser.addoption('--port'     ,action="store" ,default=8020)
    parser.addoption('--ip'       ,action="store" ,default="localhost")
    parser.addoption('--address'  ,action="store" ,default='')
    parser.addoption('--sleep'    ,action="store" ,default=0.3)
    parser.addoption('--report'   ,action='store' ,default="")#"console.log")
    parser.addoption('--headless' ,action='store_true',default=False)

    parser.addoption("--slow", action="store_true", default=False, help="run slow tests")
    parser.addoption("--opt" , action="store_true", default=False, help="run opt tests")
    parser.addoption("--old" , action="store_true", default=False, help="run old tests")
    parser.addoption("--new" , action="store_true", default=False, help="run only tests marked as new")
    parser.addoption("--lvl" , default=0, help=" test levels")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "opt: mark test as optional")
    config.addinivalue_line("markers", "old: mark test as old")
    for i in range(1,5):
        config.addinivalue_line("markers", "lvl%d: test level %d" %(i,i))
    config.addinivalue_line("markers", "new: mark test as new to run")

def skip_if_marked(config,items,marker,reason=""):
    if not reason:
        reason="Marked as {marker} test : use --{marker} option to run".format(marker=marker)
    if not config.getoption('--%s' %marker) :
        skip_test = pytest.mark.skip(reason=reason)
        for item in items:
            if marker in item.keywords:
                item.add_marker(skip_test)

def pytest_collection_modifyitems(config, items):
    if config.getoption("--new") :
        skip_all = pytest.mark.skip(reason="not a --new test")
        for item in items:
            if "new" in item.keywords:
                print('will run')
            else:
                item.add_marker(skip_all)
        return

    skip_if_marked(config,items,'slow')
    skip_if_marked(config,items,'old' )
    skip_if_marked(config,items,'opt' )

    lvl = int(config.getoption("--lvl"))
    for item in items:
        for i in range(1,5):
            if "lvl%d" %i in item.keywords:
                reason="test level marked as lvl{test_level}>{lvl}".format(test_level=i,lvl=lvl)
                item.add_marker(pytest.mark.skipif(lvl<i, reason=reason))
                break








def get_address(pytestconfig):
    if pytestconfig.getoption('address'):
        address=pytestconfig.getoption('address')
    else:
        port = pytestconfig.getoption('port')
        ip   = pytestconfig.getoption('ip')
        address = 'http://%s:%s' %(ip,port)
    return address

@pytest.fixture(scope="package")
def chrome_driver(pytestconfig):
    options = webdriver.ChromeOptions()
    if pytestconfig.getoption('headless'):
        # options.add_argument("--window-size=1920,1080")
        # options.add_argument("--start-maximized")
        options.add_argument('--headless')
    address=get_address(pytestconfig)

    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

    chrome_driver = webdriver.Chrome(options=options)
    # chrome_driver.set_network_conditions(offline=True,latency=5,throughput=500*1024)
    # print(address)
    chrome_driver.get(address)
    chrome_driver.maximize_window()

    return chrome_driver

@pytest.fixture(scope="package")
def sec(pytestconfig):
    sleep=int(pytestconfig.getoption('sleep'))
    if pytestconfig.getoption('headless'):
        sleep=0
    print(sleep)
    return sleep


@pytest.fixture(scope="package")
def port(pytestconfig):
    return pytestconfig.getoption('port')

@pytest.fixture(scope="package")
def address(pytestconfig):
    return get_address(pytestconfig)

@pytest.fixture(scope="package")
def report(pytestconfig):
    return pytestconfig.getoption('--report')
