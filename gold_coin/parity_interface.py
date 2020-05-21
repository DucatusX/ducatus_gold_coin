import json
import requests
from eth_utils import to_checksum_address
from eth_account import Account
from web3 import Web3, HTTPProvider

from gold_coin.settings import NETWORK_SETTINGS
from gold_coin.consts import DECIMALS


class ParityInterfaceException(Exception):
    pass


class ParConnectExc(Exception):
    def __init__(self, *args):
        self.value = 'can not connect to parity'

    def __str__(self):
        return self.value


class ParErrorExc(Exception):
    pass


class ParityInterface:
    endpoint = None
    settings = None

    def __init__(self):

        self.settings = NETWORK_SETTINGS['DUCX']
        self.setup_endpoint()
        # self.check_connection()

    def setup_endpoint(self):
        self.endpoint = self.settings['url']
        self.settings['chainId'] = self.eth_chainId()
        print('parity interface', self.settings, flush=True)
        return

    def __getattr__(self, method):
        def f(*args):
            arguments = {
                'method': method,
                'params': args,
                'id': 1,
                'jsonrpc': '2.0',
            }
            try:
                temp = requests.post(
                    self.endpoint,
                    json=arguments,
                    headers={'Content-Type': 'application/json'}
                )
            except requests.exceptions.ConnectionError as e:
                raise ParConnectExc()
            result = json.loads(temp.content.decode())
            if result.get('error'):
                raise ParErrorExc(result['error']['message'])
            return result['result']

        return f

    def transfer(self, address, weight, user_key, purchase_date, origin):
        print('DUCATUSX ERC721 TOKEN MINT STARTED: {address}'.format(
            address=address,
        ), flush=True)

        nonce = self.eth_getTransactionCount(self.settings['address'], "pending")
        gas_price = self.eth_gasPrice()
        chain_id = self.settings['chainId']

        tx_params = {
            'gas': 500000,
            'gasPrice': int(gas_price, 16) * 2,
            'nonce': int(nonce, 16),
            'chainId': int(chain_id, 16)
        }
        print('TX PARAMS', tx_params, flush=True)

        try:
            w3 = Web3(HTTPProvider(self.endpoint))
            contract = w3.eth.contract(address=self.settings['contract_address'], abi=self.settings['abi'])
            token_id = contract.functions.totalSupply().call() + 1
            tx_data = contract.functions._mint(to_checksum_address(address), token_id, weight, purchase_date, origin,
                                               '0x' + user_key).buildTransaction(tx_params)

            signed = w3.eth.account.signTransaction(tx_data, self.settings['private'])
            print('signed_tx', signed)

            sent = self.eth_sendRawTransaction(signed.rawTransaction.hex())
            print('TXID:', sent, flush=True)
            return sent, token_id
        except Exception as e:
            err = 'DUCATUSX ERC721 MINT ERROR: transfer for {addr} failed' \
                .format(addr=address)
            print(err, flush=True)
            print(e, flush=True)
            raise ParityInterfaceException(err)
