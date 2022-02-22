
def get_main_wallet():
    with open('../seed/main_wallet.txt', 'r') as file:
        _main_wallet = [row.strip() for row in file]
    return _main_wallet


def get_wallets():
    with open('../seed/wallets.txt', 'r') as file:
        _wallets = [row.strip() for row in file]
    return _wallets
