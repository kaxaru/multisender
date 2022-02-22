from polygonscan import PolygonScan
from bscscan import BscScan
from etherscan import Etherscan

API_KEY_POLYGON = '1RBB36K6QB7EQRSYG2QHWCWXY8TPY949VG'
API_KEY_BSC = 'Q4X54V2YJ44IVQWYNFVSFE1ZNRKAWTJ8FX'
API_KEY_ETH = '9EVUW7BFD4BZ16TFJSU3QC5DHYDC3JQHVF'

providers = {
    'matic': {'chainId': 137,
              "rpc": 'https://polygon-rpc.com'},
    'bsc': {'chainId': 56,
            "rpc": 'https://bsc-dataseed.binance.org/'},
    'eth': {'chainId': 1,
            "rpc": 'https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'}
}

def get_default_providers():
    return providers['matic']


def get_providers(chain):
    default_provider = get_default_providers()
    if chain == 1:
        default_provider = {'provider': providers['eth'], 'api_key': API_KEY_ETH}
    elif chain == 2:
        default_provider = {'provider': providers['bsc'], 'api_key': API_KEY_BSC}
    else:
        default_provider = {'provider': providers['matic'], 'api_key': API_KEY_POLYGON}

    return default_provider


def install_scanner(provider):
    _scanner = ''
    if provider['chainId'] == providers['matic']['chainId']:
        _scanner = PolygonScan(api_key=API_KEY_POLYGON, asynchronous=False)
    elif provider['chainId'] == providers['bsc']['chainId']:
        _scanner = BscScan(api_key=API_KEY_BSC, asynchronous=False)
    else:
        _scanner = Etherscan(api_key=API_KEY_ETH)
    _scanner.__enter__()
    return _scanner
