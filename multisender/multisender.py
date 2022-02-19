import threading
from threading import Thread
from web3 import Web3
from eth_account import Account
from loguru import logger
from sys import stderr
from os import system
from ctypes import windll
from urllib3 import disable_warnings


import metamask_wallets
import API_KEY
import contract_asset

disable_warnings()
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - "
                          "<white>{message}</white>")
system('cls')

windll.kernel32.SetConsoleTitleW('Multisender onchain')
lock = threading.Lock()

default_provider = API_KEY.get_default_providers()

main_wallet = metamask_wallets.get_main_wallet()
wallets = metamask_wallets.get_wallets()

num_of_acc = int(input('How many accs?: '))
gas_price = float(input('Gas price: '))

send_token_or_asset = int(input('1 - def: main token, 2 - optional - asset '))
if send_token_or_asset == 2:
    send_option_asset = int(input('1 - into wallets, 2 - from wallets '))
else:
    send_option_asset = 1

send_how_much = 0.001
option_how_much_token =int(input('1 - def: 0.001, 2 - optional in gwei '))

if option_how_much_token == 2:
    send_how_much = float(input('How much tokens? '))

threads = int(input('Threads: '))
wait_tx_result = str(input('Wait TX result? (y/N): '))


def sign_and_confirm(transaction, private_key, address_from, address_to, acc_num, nonce):
    s_tx = web3.eth.account.signTransaction(transaction, private_key)
    tx_hash = web3.eth.sendRawTransaction(s_tx.rawTransaction)
    logger.info(f'TX id: {web3.toHex(tx_hash)}  address from: {address_from}; address to {address_to} acc: {acc_num} '
                f'nonce: {nonce}')
    if wait_tx_result in ('y', 'Y'):
        tx_status = web3.eth.waitForTransactionReceipt(tx_hash).status
        if tx_status == 1:
            logger.success(f'TX status: {tx_status}')
        else:
            logger.error(f'TX status: {tx_status}')


def sendToken(main_address, address_to, provider, nonce, acc_num):
    try:
        transaction = {
            "chainId": provider['chainId'],
            'to': address_to.address,
            'value': web3.toWei(str(send_how_much), 'ether'),
            'gas': 21000,
            'gasPrice': web3.toWei(str(gas_price), 'gwei'),
            'nonce': nonce + acc_num,
        }

        sign_and_confirm(transaction, main_address.privateKey, main_address.address, address_to.address, acc_num, nonce)

    except Exception as error:
        if 'Too Many Requests for url' in str(error):
            Account.mainth(main_address.privateKey)
        else:
            logger.error(f'Error: {str(error)}')


def sendAsset(main_address, address_to, send_option_asset, provider, nonce, acc_num):
    try:
        address_from = main_address.address
        address_to_ = address_to.address
        balance = web3.toWei(str(send_how_much), 'mwei')
        private_key_from = main_address.privateKey

        # Option: 1) address to wallets
        #         2) wallets to address
        if send_option_asset == 2:
            address_to_ = main_address.address
            address_from = address_to.address
            balance_on_wallet = contract.functions.balanceOf(address_from).call()
            private_key_from = address_to.privateKey
            if balance_on_wallet < balance:
                balance = balance_on_wallet

        transaction = contract.functions.transfer(address_to_, balance).buildTransaction({
            "chainId": provider['chainId'],
            'gas': 120000,
            'gasPrice': web3.toWei(gas_price, 'gwei'),
            'from': address_from,
            'nonce': nonce
        })

        if balance > 0:
            sign_and_confirm(transaction, private_key_from, address_from, address_to_, acc_num, nonce)

    except Exception as error:
        if 'Too Many Requests for url' in str(error):
            Account.mainth(main_address.privateKey)
        else:
            logger.error(f'Error: {str(error)}')


if __name__ == '__main__':
    system('cls')
    chain = int(input('1 - eth, 2 - bsc, 3 - matic: '))
    default_provider = API_KEY.get_providers(chain)

    # ...number of mnemonic in file?
    mnemonic_for_receive = 0
    web3 = Web3(Web3.HTTPProvider(default_provider['provider']['rpc']))
    web3.eth.account.enable_unaudited_hdwallet_features()
    main_address = web3.eth.account.from_mnemonic(main_wallet.pop(0), account_path="m/44'/60'/0'/0/0")
    cNonce_main_wallet = web3.eth.get_transaction_count(main_address.address)

    if send_token_or_asset == 2:
        scanner = API_KEY.install_scanner(default_provider['chainId'])
        option_contract_asset = int(input('Options: 1 - in list, 2 - input contract: '))
        if option_contract_asset == 1:
            contract_list = int(input('1 - usdt, 2 - usdc  '))
            asset_name = contract_asset.get_asset_from_list(contract_list)
            try:
                contract_address = contract_asset.get_asset_address(asset_name, default_provider['chainId'])
            except Exception as error:
                logger.error(f'not found asset: {str(error)}')
        else:
            contract_address = str(input('input contract adress:  0x............'))
        if type(contract_address) is str:
            abi = scanner.get_contract_abi(contract_address)
            contract = web3.eth.contract(address=web3.toChecksumAddress(contract_address),
                                         abi=abi)

        if 'implementation' in [func for func in contract.functions]:
            contract_address_proxy = contract.functions.implementation().call()
            proxy_abi = scanner.get_contract_abi(contract_address_proxy)
            contract = web3.eth.contract(address=web3.toChecksumAddress(contract_address),
                                       abi=proxy_abi)

    while wallets:
        mnemonic = wallets.pop(0);
        acc_num = 0
        mnemonic_for_receive += 1
        while acc_num < num_of_acc:
            if threading.active_count() <= threads:
                for thread in range(threads):
                    account_path = "m/44'/60'/0'/0/{acc_num}".format(acc_num=acc_num)
                    address_to = web3.eth.account.from_mnemonic(mnemonic, account_path=account_path)
                    if send_option_asset == 2:
                        nonce = web3.eth.get_transaction_count(address_to.address)
                    else:
                        delta_cNonce_main_wallet = (mnemonic_for_receive - 1) * num_of_acc + acc_num
                        nonce = delta_cNonce_main_wallet + cNonce_main_wallet
                    if send_token_or_asset == 1:
                        Thread(target=sendToken,
                               args=(main_address, address_to, default_provider['provider'], nonce, acc_num)).start()
                    else:
                        Thread(target=sendAsset,
                               args=(main_address, address_to, send_option_asset, default_provider['provider'], nonce, acc_num)).start()
                    acc_num += 1
