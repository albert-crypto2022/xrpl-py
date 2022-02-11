# Define the network client
from xrpl.clients import JsonRpcClient
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)


# Create a wallet using the testnet faucet:
# https://xrpl.org/xrp-testnet-faucet.html
from xrpl.wallet import generate_faucet_wallet
test_wallet = generate_faucet_wallet(client, debug=True)

# Create an account str from the wallet
test_account = test_wallet.classic_address

# Derive an x-address from the classic address:
# https://xrpaddress.info/
from xrpl.core import addresscodec
test_xaddress = addresscodec.classic_address_to_xaddress(test_account, tag=12345, is_test_network=True)
print("\nClassic address:\n\n", test_account)
print("X-address:\n\n", test_xaddress)


# Look up info about your account
from xrpl.models.requests.account_info import AccountInfo
acct_info = AccountInfo(
    account=test_account,
    ledger_index="validated",
    strict=True,
)
response = client.request(acct_info)
result = response.result
print("response.status: ", response.status)
import json
print(json.dumps(response.result, indent=4, sort_keys=True))

# Check cash
from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
# from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import CheckCash

# ACCOUNT = WALLET.classic_address
ACCOUNT = test_wallet.classic_address
CHECK_ID = "838766BA2B995C00744175F69A1B11E32C3DBC40E64801A4056FCBD657F57334"
AMOUNT = "100000000"
DELIVER_MIN = "100000000"


check_cash = CheckCash(
    account=ACCOUNT,
    sequence=test_wallet.sequence,
    check_id=CHECK_ID,
    amount=AMOUNT,
    #amount=test_wallet.Balance,
)
# response = client.request(check_cash)
# result = response.result
# print("response.status: ", response.status)
# import json
# print(json.dumps(response.result, indent=4, sort_keys=True))

print ("check_cash = ", check_cash)
#print ("check_cash = ", json.dumps(check_cash))

# # get fee
# from xrpl.ledger import get_fee
# fee = get_fee(client)
# print("XRPL fee = ", fee)
# # 10

# serialize and sign the transaction
from xrpl.models.transactions import Payment
from xrpl.transaction import safe_sign_transaction, send_reliable_submission
from xrpl.ledger import get_latest_validated_ledger_sequence
from xrpl.account import get_next_valid_seq_number

current_validated_ledger = get_latest_validated_ledger_sequence(client)
test_wallet.sequence = get_next_valid_seq_number(test_wallet.classic_address, client)

print ("\n\ncurrent_validated_ledger ", current_validated_ledger   )
print ("test_wallet.sequence ", test_wallet.sequence)
# prepare the transaction
# the amount is expressed in drops, not XRP
# see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
my_tx_payment = Payment(
    account=test_wallet.classic_address,
    #amount="2200000",
    amount="2212345",
    destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
    last_ledger_sequence=current_validated_ledger + 20,
    sequence=test_wallet.sequence,
    fee="10",
)
print ("\n\nmy_tx_payment ", my_tx_payment)

# sign the transaction
my_tx_payment_signed = safe_sign_transaction(my_tx_payment,test_wallet)
print ("\n\nmy_tx_payment_signed ", my_tx_payment_signed)

# submit the transaction
tx_response = send_reliable_submission(my_tx_payment_signed, client)
print ("\n\ntx_response ", tx_response)


from xrpl.clients import WebsocketClient
url = "wss://s.altnet.rippletest.net/"
from xrpl.models.requests import Subscribe, StreamParameter
req = Subscribe(streams=[StreamParameter.LEDGER])
# NOTE: this code will run forever without a timeout, until the process is killed
with WebsocketClient(url) as client:
    client.send(req)
    print ("\n\nGet Last XRPL Ledger Update")
    ledger_updates_count = 0
    for message in client:
        print(message)
        ledger_updates_count += 1
        if ledger_updates_count > 0:
            break
# {'result': {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': '7CD50477F23FF158B430772D8E82A961376A7B40E13C695AA849811EDF66C5C0', 'ledger_index': 18183504, 'ledger_time': 676412962, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'validated_ledgers': '17469391-18183504'}, 'status': 'success', 'type': 'response'}
# {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': 'BAA743DABD168BD434804416C8087B7BDEF7E6D7EAD412B9102281DD83B10D00', 'ledger_index': 18183505, 'ledger_time': 676412970, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'txn_count': 0, 'type': 'ledgerClosed', 'validated_ledgers': '17469391-18183505'}
# {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': 'D8227DAF8F745AE3F907B251D40B4081E019D013ABC23B68C0B1431DBADA1A46', 'ledger_index': 18183506, 'ledger_time': 676412971, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'txn_count': 0, 'type': 'ledgerClosed', 'validated_ledgers': '17469391-18183506'}
# {'fee_base': 10, 'fee_ref': 10, 'ledger_hash': 'CFC412B6DDB9A402662832A781C23F0F2E842EAE6CFC539FEEB287318092C0DE', 'ledger_index': 18183507, 'ledger_time': 676412972, 'reserve_base': 20000000, 'reserve_inc': 5000000, 'txn_count': 0, 'type': 'ledgerClosed', 'validated_ledgers': '17469391-18183507'}


import asyncio
from xrpl.models.transactions import Payment
from xrpl.asyncio.transaction import safe_sign_transaction, send_reliable_submission
from xrpl.asyncio.ledger import get_latest_validated_ledger_sequence
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.clients import AsyncJsonRpcClient

async_client = AsyncJsonRpcClient(JSON_RPC_URL)
print ("\n\nasync_client = ", async_client)
async def submit_sample_transaction():
    current_validated_ledger = await get_latest_validated_ledger_sequence(async_client)
    test_wallet.sequence = await get_next_valid_seq_number(test_wallet.classic_address, async_client)

    # prepare the transaction
    # the amount is expressed in drops, not XRP
    # see https://xrpl.org/basic-data-types.html#specifying-currency-amounts
    my_tx_payment = Payment(
        account=test_wallet.classic_address,
        amount="2211223",
        destination="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
        last_ledger_sequence=current_validated_ledger + 20,
        sequence=test_wallet.sequence,
        fee="10",
    )
    # sign the transaction
    my_tx_payment_signed = await safe_sign_transaction(my_tx_payment,test_wallet)

    # submit the transaction
    tx_response = await send_reliable_submission(my_tx_payment_signed, async_client)

    print ("\n\ntx_response = ", tx_response)
asyncio.run(submit_sample_transaction())


IntegrationTestCase = []
class TestCheckCreate():
#class TestCheckCreate(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_required_fields_with_amount(self, client):
        check_cash = CheckCash(
            account=ACCOUNT,
            sequence=test_wallet.sequence,
            check_id=CHECK_ID,
            amount=AMOUNT,
        )
        response = await submit_transaction_async(check_cash, test_wallet)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        # Getting `tecNO_ENTRY` codes because using a non-existent check ID
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")
        test_wallet.sequence += 1

    @test_async_and_sync(globals())
    async def test_required_fields_with_deliver_min(self, client):
        check_cash = CheckCash(
            account=ACCOUNT,
            sequence=test_wallet.sequence,
            check_id=CHECK_ID,
            deliver_min=DELIVER_MIN,
        )
        response = await submit_transaction_async(check_cash, test_wallet)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tecNO_ENTRY")
        test_wallet.sequence += 1
#TestCheckCreate()

class XrpClient(object):

    def __init__(self):
        self.accountID = None
        self.account = None
        self.user_email = None

        self.BENEFICIARY_ADDRESS_1 = BENEFICIARY_ADDRESS_1
        self.BENEFICIARY_KEY_1 = BENEFICIARY_KEY_1
        self.BENEFICIARY_ADDRESS_2 = BENEFICIARY_ADDRESS_2
        self.BENEFICIARY_KEY_2 = BENEFICIARY_KEY_2
        self.BENEFICIARY_ADDRESS_3 = BENEFICIARY_ADDRESS_3
        self.BENEFICIARY_KEY_3 = BENEFICIARY_KEY_3

        self._remote = None
        self._remote = Remote(XRP_API_URL, self.BENEFICIARY_ADDRESS_1)

    def from_account(self, account=None):
        self.account = account
        if not self.account:
            raise ValueError('Missing Ripple Setup Variable: {}'.format('Account'))
        return self

    def from_accountID(self, accountID=None):
        self.accountID = accountID
        if not self.accountID:
            raise ValueError('Missing Ripple Setup Variable: {}'.format('Account ID'))

        self.account = get_account([], accountID)
        if not self.account:
            raise ValueError('Missing Ripple Setup Variable: {}'.format('Account'))
        return self

    def get_flare_faucet_address(self, pubKey=None):
        # return get_ripple_from_pubkey(pubKey)
        return get_ripple_from_pubkey(b'C1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')

    def is_classic_address(self, address, tag=None):
        return True
        r = requests.get(url='https://xrpaddress.info/api/encode/{}/{}'.format(address, tag))
        if 'error' in r.json():
            return False
        return True

    def is_x_address(self, address):
        r = requests.get(url='https://xrpaddress.info/api/decode/{}'.format(address))
        if 'error' in r.json():
            return False
        return True

    def encode_classic_address(self, address, tag):
        r = requests.get(url='https://xrpaddress.info/api/encode/{}/{}'.format(address, tag))
        return r.json()

    def decode_x_address(self, address):
        r = requests.get(url='https://xrpaddress.info/api/decode/{}'.format(address))
        return r.json()

    def convert_address_to_classic(self, destination):
        if self.is_x_address(destination):
            return self.decode_x_address(destination)['account']
        if self.is_classic_address(destination):
            return destination

    def mint(self):
        r = requests.post(url='https://faucet.altnet.rippletest.net/accounts')
        json_data = r.json()
        return json_data["account"]["secret"], json_data["balance"]

    def mint_injection(self):
        secret, amount = self.mint()
        sender = get_ripple_from_secret(secret)
        tx = self.build(sender, self.BENEFICIARY_ADDRESS_1, amount - 20)
        signed_tx = self.sign(tx, secret)
        return self._remote.client.submit(tx_blob=signed_tx)

    def mint_submit(self, to=None, value=50):
        sender = get_ripple_from_secret(self.BENEFICIARY_KEY_1)
        tx = self.build(sender, to, value)
        signed_tx = self.sign(tx, self.BENEFICIARY_KEY_1)
        return self.submit(tx_blob=signed_tx)

    def build_evm(self, sender=None, to=None, value=50):
        # Construct the basic transaction
        tx = {
            "TransactionType": "Payment",
            "Account": sender,
            "Destination": self.convert_address_to_classic(self.get_flare_faucet_address()),
            "Amount": Amount('{:0.2f}'.format(Decimal(value))),
        }

        self._remote.client.add_fee(tx)

        # We need to determine the sequence number
        sequence = self._remote.account_info(sender)['Sequence']
        tx['Sequence'] = sequence
        tx['Memos'] = [{'Memo': {'MemoData': fxrp}}]
        return tx

    def full(self, seed, sender, destination, amount):
        tx = self.build(sender=sender, to=destination, value=amount)
        signed_tx = self.sign(tx, seed)
        return self._remote.client.submit(tx_blob=signed_tx)

    def build(self, sender=None, to=None, value=0):
        # Construct the basic transaction
        tx = {
            "TransactionType": "Payment",
            "Account": sender,
            "Destination": to,
            "Amount": Amount('{:0.2f}'.format(Decimal(value))),
        }

        self._remote.client.add_fee(tx)

        # We need to determine the sequence number
        sequence = self._remote.account_info(sender)['Sequence']
        tx['Sequence'] = sequence
        return tx

    def sign(self, tx=None, key=None):
        return sign_transaction(tx, key)

    def submit(self, tx_blob=None):
        return self._remote.client.submit(tx_blob=tx_blob)