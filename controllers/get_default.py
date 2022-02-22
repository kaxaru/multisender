from seed import default
from loguru import logger


def get_default_value(param_name):
    try:
        match param_name:
            case 'send_token_or_asset':
                value = int(input('1 - def: main token, 2 - optional - asset '))
                if (type(value) == int) and (value > 0) and (value <= 2):
                    return value
                else:
                    return default.params['send_token_or_asset']
            case 'num_of_acc':
                return int(input('How many accs?: '))
            case 'gas_price':
                return int(input('Gas price: '))
            case 'send_option_asset':
                value = int(input('1 - into wallets, 2 - from wallets '))
                if (type(value) == int) and (value > 0) and (value <= 2):
                    return value
                else:
                    return default.params['send_option_asset']
            case 'option_how_much_token':
                value = float(input('1 - def: 0.001, 2 - optional in gwei '))
                if (type(value) == int) and (value > 0) and (value <= 2):
                    return value
                else:
                    return default.params['option_how_much_token']
            case 'send_how_much':
                return float(input('How much tokens? '))
            case 'threads':
                return int(input('Threads: '))
            case 'wait_tx_result':
                return str(input('Wait TX result? (y/N): '))
            case 'option_contract_asset':
                value = int(input('Options: 1 - in list, 2 - input contract: '))
                if (type(value) == int) and (value > 0) and (value <= 2):
                    return value
                else:
                    return default.params['option_contract_asset']

    except Exception as error:
        logger.error(f'Error: {str(error)}')
        logger.error(f'param name: {str(param_name)}, value - {str(value)}')