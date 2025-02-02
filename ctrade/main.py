import logging
from pathlib import Path
from typing import Any
from ctrade.configuration.configs import (
    start_new_config,
)
from freqtrade import __version__
from freqtrade.commands import (
    start_create_userdir,
    start_trading,
    start_install_ui,
    start_download_data,
)
from freqtrade.loggers import setup_logging_pre

logger = logging.getLogger(__name__)

def main() -> None:
    setup_logging_pre()
    logger.info(f"freqtrade {__version__}")
    default_args = {
        "dry_run": True,
        "user_data_dir": "user/data",
        "config": ["user/config.json"],
        "pair_config": "user/pairs.json",
        "pairs": ["CWA/USDT"],
    }
    start_create_userdir(default_args | {"reset": False})
    start_new_config(default_args | {"overwrite": False})
    if not Path("freqtrade/rpc/api_server/ui/installed/.uiversion").exists():
        start_install_ui({})
    #start_download_data(default_args | { "download_trades": False, "days": 30, "datadir" : "user/history" })
    start_trading(default_args | {"strategy": "SampleStrategy"})

if __name__ == "__main__":
    main()