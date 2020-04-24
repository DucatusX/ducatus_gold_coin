from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound

from gold_coin.coin_info.models import TokenInfo
from gold_coin.transfer.models import DucatusTransfer, ErcTransfer


class DucatusTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DucatusTransfer
        fields = ['amount', 'tx_hash', 'transfer_status']


class ErcTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DucatusTransfer
        fields = ['amount', 'tx_hash', 'transfer_status']


class TokenInfoSerializer(serializers.ModelSerializer):
    ducatustransfer = DucatusTransferSerializer()
    erctransfer = ErcTransferSerializer()

    class Meta:
        model = TokenInfo
        fields = ('public_code', 'ducatus_address', 'ducatusx_address', 'token_type', 'is_active', 'mint_date',
                  'country', 'certified_assayer', 'purchase_date', 'token_id', 'duc_value', 'gold_price',
                  'production_date', 'ducatustransfer', 'erctransfer')


    def validate(self, data):
        data['secret_code'] = self.key_format(data['secret_code'])
        secret_code = data['secret_code']
        coin = TokenInfo.objects.filter(secret_code=secret_code).first()
        if not coin:
            raise NotFound(
                detail='coin with secret_code={secret_code} not exist'.format(secret_code=secret_code))
        if coin.is_active:
            raise PermissionDenied(
                detail='coin with secret_code={secret_code} has already registered'.format(secret_code=secret_code))
        data['ducatusx_address'] = data['ducatusx_address'].lower()
        data['is_active'] = True
        return data

    @staticmethod
    def key_format(key):
        return ''.join(key.split('-'))
