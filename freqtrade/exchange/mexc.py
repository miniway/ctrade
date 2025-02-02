
from freqtrade.exchange.common import retrier
from freqtrade.exchange.exchange import Exchange
from freqtrade.exchange.exchange_types import FtHas


class Mexc(Exchange):
    # Name of the exchange
    name = 'mexc'

    # Timeframe for the exchange
    timeframe = '5m'

    # Default API Interface
    api_interface = 'REST'

    _ft_has: FtHas = {
        "stoploss_order_types": {"limit": "limit"},
        "stoploss_on_exchange": True,
        "trades_has_history": False,  # Endpoint doesn't have a "until" parameter
    }

    @retrier
    def additional_exchange_init(self) -> None:
        pass