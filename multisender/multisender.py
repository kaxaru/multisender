import threading
from threading import Thread
from web3 import Web3
from eth_account import Account
from loguru import logger
from sys import stderr
from os import system
from ctypes import windll
from urllib3 import disable_warnings

from seed import default
from controllers import get_default
from controllers import metamask_wallets, API_KEY
import contract_asset
import copy

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

setup_params = copy.deepcopy(default.params)

setup_params['num_of_acc'] = get_default.get_default_value('num_of_acc')
setup_params['gas_price'] = get_default.get_default_value('gas_price')
setup_params['send_token_or_asset'] = get_default.get_default_value('send_token_or_asset')
if setup_params['send_token_or_asset'] != default.params['send_token_or_asset']:
    setup_params['send_option_asset'] = get_default.get_default_value('send_option_asset')

setup_params['option_how_much_token'] = get_default.get_default_value('option_how_much_token')

if setup_params['option_how_much_token'] != default.params['option_how_much_token']:
    setup_params['send_how_much'] = get_default.get_default_value('send_how_much')

setup_params['threads'] = get_default.get_default_value('threads')
setup_params['wait_tx_result'] = get_default.get_default_value('wait_tx_result')


def sign_and_confirm(transaction, private_key, address_from, address_to, acc_num, nonce):
    s_tx = web3.eth.account.signTransaction(transaction, private_key)
    tx_hash = web3.eth.sendRawTransaction(s_tx.rawTransaction)
    logger.info(f'TX id: {web3.toHex(tx_hash)}  address from: {address_from}; address to {address_to} acc: {acc_num} '
                f'nonce: {nonce}')
    if setup_params['wait_tx_result'] in ('y', 'Y'):
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
            'value': web3.toWei(str(default.params['send_how_much']), 'ether'),
            'gas': 21000,
            'gasPrice': web3.toWei(str(setup_params['gas_price']), 'gwei'),
            'nonce': nonce + acc_num,
        }

        sign_and_confirm(transaction, main_address.privateKey, main_address.address, address_to.address, acc_num, nonce)

    except Exception as error:
        if 'Too Many Requests for url' in str(error):
            Account.mainth(main_address.privateKey)
        else:
            logger.error(f'Error: {str(error)}')


def sendAsset(main_address, address_to, provider, nonce, acc_num):
    try:
        address_from = main_address.address
        address_to_ = address_to.address
        balance = web3.toWei(str(default.params['send_how_much']), 'mwei')
        private_key_from = main_address.privateKey

        # Option: 1) address to wallets
        #         2) wallets to address
        if setup_params['send_option_asset'] != default.params['send_option_asset']:
            address_to_ = main_address.address
            address_from = address_to.address
            balance_on_wallet = contract.functions.balanceOf(address_from).call()
            private_key_from = address_to.privateKey
            if balance_on_wallet < balance:
                balance = balance_on_wallet

        transaction = contract.functions.transfer(address_to_, balance).buildTransaction({
            "chainId": provider['chainId'],
            'gas': 120000,
            'gasPrice': web3.toWei(setup_params['gas_price'], 'gwei'),
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

    if setup_params['send_token_or_asset'] != default.params['send_token_or_asset']:
        scanner = API_KEY.install_scanner(default_provider['chainId'])
        setup_params['option_contract_asset'] = get_default.get_default_value('option_contract_asset')
        if setup_params['option_contract_asset'] == default.params['option_contract_asset']:
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
        while acc_num < setup_params['num_of_acc']:
            if threading.active_count() <= setup_params['threads']:
                for thread in range(setup_params['threads']):
                    account_path = "m/44'/60'/0'/0/{acc_num}".format(acc_num=acc_num)
                    address_to = web3.eth.account.from_mnemonic(mnemonic, account_path=account_path)
                    if setup_params['send_option_asset'] != default.params['send_option_asset']:
                        nonce = web3.eth.get_transaction_count(address_to.address)
                    else:
                        delta_cNonce_main_wallet = (mnemonic_for_receive - 1) * setup_params['num_of_acc'] + acc_num
                        nonce = delta_cNonce_main_wallet + cNonce_main_wallet
                    if setup_params['send_token_or_asset'] == default.params['send_token_or_asset']:
                        Thread(target=sendToken,
                               args=(main_address, address_to, default_provider['provider'], nonce, acc_num)).start()
                    else:
                        Thread(target=sendAsset,
                               args=(main_address, address_to,
                                     default_provider['provider'], nonce, acc_num)).start()
                    acc_num += 1
