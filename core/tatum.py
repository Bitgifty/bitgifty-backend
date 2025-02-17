import requests
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CurrencyPair:
    base: str
    quote: str


class TatumExchangeRates:
    def __init__(self, api_key: str):
        """
        Initialize Tatum Exchange Rates client

        Args:
            api_key (str): Your Tatum API key
        """
        self.api_key = api_key
        self.base_url = "https://api.tatum.io/v3"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def get_exchange_rate(self, currency1: str, currency2: str) -> float:
        """
        Get current exchange rate between two currencies

        Args:
            currency1 (str): Base currency code (e.g., 'BTC', 'ETH', 'USD')
            currency2 (str): Quote currency code

        Returns:
            float: Exchange rate

        Raises:
            ValueError: If invalid currency codes provided
            RequestException: If API request fails
        """
        try:
            url = f"{self.base_url}/tatum/rate/{currency1}"
            base_pair = f"?basePair={currency2}"
            response = requests.get(url+base_pair, headers=self.headers)
            response.raise_for_status()
            return float(response.json().get("value"))

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                raise ValueError(
                    f"Invalid currency pair: {currency1}/{currency2}"
                )
            elif e.response.status_code == 401:
                raise ValueError("Invalid API key")
            elif e.response.status_code == 429:
                raise ValueError("Rate limit exceeded")
            else:
                raise requests.exceptions.RequestException(
                    f"API request failed: {str(e)}"
                )

        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid response format: {str(e)}")

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Request failed: {str(e)}"
            )

    def get_batch_rates(
        self,
        pairs: List[CurrencyPair]
    ) -> Dict[str, Optional[float]]:
        """
        Get exchange rates for multiple currency pairs

        Args:
            pairs (List[CurrencyPair]): List of currency pairs to fetch

        Returns:
            Dict[str, Optional[float]]: Dictionary of exchange rates with
                pair strings as keys (e.g., 'BTC/USD') and rates as values.
                Failed pairs will have None as value.
        """
        results = {}

        for pair in pairs:
            pair_str = f"{pair.base}/{pair.quote}"
            try:
                rate = self.get_exchange_rate(pair.base, pair.quote)
                results[pair_str] = rate
            except Exception as e:
                print(f"Failed to fetch rate for {pair_str}: {str(e)}")
                results[pair_str] = None

        return results
