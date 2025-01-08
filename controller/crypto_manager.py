import os
from typing import Dict, Optional

import requests

from base_models.cryptocurrency_base import CryptoToken, TransactionDetails


class CryptoManager:
    def __init__(self):
        self.api_key = os.getenv('COIN_MARKET_CAP_API')
        self.supported_currencies: Dict[str, CryptoToken] = {}
        self.last_update: Optional[float] = None
        self.update_interval = 300  # Update every 5 minutes
        self.CABL_PRICE_USD = 0.05  # Fixed CABL price

    async def update_supported_currencies(self):
        """Fetch and update the list of supported currencies from CoinMarketCap"""
        print('Updating supported cryptos...')
        try:
            # Get listings with market data
            listings_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
            headers = {'X-CMC_PRO_API_KEY': self.api_key}
            params = {'limit': 25, 'convert': 'USD'}

            response = requests.get(listings_url, headers=headers, params=params)
            listings_data = response.json()

            # Get metadata including logos
            ids = ','.join(str(token['id']) for token in listings_data['data'])
            metadata_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
            metadata_params = {'id': ids}
            metadata_response = requests.get(metadata_url, headers=headers, params=metadata_params)
            metadata = metadata_response.json()

            # Update supported currencies
            self.supported_currencies.clear()
            for token in listings_data['data']:
                token_id = str(token['id'])
                token_metadata = metadata['data'][token_id]


                crypto_token = CryptoToken(
                    id=token_id,
                    symbol=token['symbol'],
                    name=token['name'],
                    price=token['quote']['USD']['price'],
                    logo=token_metadata['logo'],
                )
                self.supported_currencies[token['symbol']] = crypto_token

            print(f"Updated supported currencies with addresses:")
            for symbol, token in self.supported_currencies.items():
                print(f"{symbol}: {token.address or 'No address'}")

            return True

        except Exception as e:
            print(f"Error updating supported currencies: {e}")
            return False

    def get_network_fee(self, currency: str) -> float:
        """Get estimated network fee for different cryptocurrencies"""
        network_fees = {
            'BTC': 2.50,    # Bitcoin transaction fee
            'ETH': 1.50,    # Ethereum gas fee
            'BNB': 0.30,    # BNB Smart Chain fee
            'USDT': 1.50,   # USDT on Ethereum
            'USDC': 1.50,   # USDC on Ethereum
            'SOL': 0.01,    # Solana fee
        }
        return network_fees.get(currency, 1.00)

    async def get_transaction_details(self, currency: str, amount: float) -> TransactionDetails:
        """Calculate transaction details for purchasing CABL tokens"""
        try:
            if currency not in self.supported_currencies:
                raise ValueError("Unsupported currency")

            token = self.supported_currencies[currency]

            # Calculate USD value and CABL amount
            input_value_usd = amount * token.price
            cabl_amount = input_value_usd / self.CABL_PRICE_USD

            # Calculate fees
            network_fee_usd = self.get_network_fee(currency)
            network_fee_crypto = network_fee_usd / token.price

            # Calculate total cost
            total_cost = amount + network_fee_crypto

            return TransactionDetails(
                estimatedAmount=cabl_amount,
                networkFee=network_fee_crypto,
                totalCost=total_cost,
                pricePerToken=self.CABL_PRICE_USD,
                inputCurrency=currency
            )

        except Exception as e:
            print(f"Error calculating transaction details: {e}")
            raise
