list_of_asset = {
    1: 'usdt',
    2: 'usdc'
}

contract_address = {
    'usdt': {
        137: '0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
        56: '0x55d398326f99059ff775485246999027b3197955',
        1: '0xdac17f958d2ee523a2206206994597c13d831ec7'
    },
    'usdc': {
            137: '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
            56: '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
            1: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
        }
}

def get_asset_from_list(num):
    try:
        _asset = list_of_asset[num]
    except TypeError as t_err:
        print("error type =", t_err)
        print("what's wrong, default value 0 [usdt]")
        _asset = list_of_asset[0]

    return _asset

def get_asset_address(name, provider_chainId):
    return contract_address[name][provider_chainId]

