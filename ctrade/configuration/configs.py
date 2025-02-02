
import logging
import json
from pathlib import Path
from freqtrade.constants import UNLIMITED_STAKE_AMOUNT

from freqtrade.enums import TradingMode
from ctrade.util.template_renderer import render_template as render_template_custom

logger = logging.getLogger(__name__)

def default_config(args: dict[str, any]) -> dict[str, any]:
    dry_run = args.get("dry_run", True)
    pair_path : Path = Path(args["pair_config"])
    pairs : list[str] = args["pairs"]
    configs = {
        "dry_run": dry_run,
        "stake_currency": "USDT",
        "stake_amount" : 1000,
        "trading_mode": TradingMode.SPOT,
        "max_open_trades": 3,
        "timeframe": "5m",
        "exchange_name" : "mexc",
        "exchange_key": "",
        "exchange_secret": "",
        "api_server": True,
        "api_server_listen_addr": "0.0.0.0",
        "api_server_listen_port": 8080,
        "api_server_username": "admin",
        "api_server_password": "admin",
        "telegram" : False,
        "pairlist" : f"""{{
            "method": "RemotePairList",
            "number_assets": {len(pairs)},
            "pairlist_url" : "file:///{pair_path.absolute()}"
        }}"""
    }
    return configs

def deploy_new_pairs(pair_path: Path, pairs: list[str]) -> None:
    data = {
        "pairs": json.dumps(pairs),
        "number_assets": len(pairs),
    }
    config_text = render_template_custom(templatefile="base_pairs.json.j2", arguments=data)
    pair_path.write_text(config_text)

def deploy_new_config(config_path: Path, selections: dict[str, any]) -> None:
    """
    Applies selections to the template and writes the result to config_path
    :param config_path: Path object for new config file. Should not exist yet
    :param selections: Dict containing selections taken by the user.
    """
    from jinja2.exceptions import TemplateNotFound

    from freqtrade.exchange import MAP_EXCHANGE_CHILDCLASS
    from freqtrade.util import render_template

    try:
        exchange_template = MAP_EXCHANGE_CHILDCLASS.get(
            selections["exchange_name"], selections["exchange_name"]
        )

        selections["exchange"] = render_template(
            templatefile=f"subtemplates/exchange_{exchange_template}.j2", arguments=selections
        )
    except TemplateNotFound:
        selections["exchange"] = render_template(
            templatefile="subtemplates/exchange_generic.j2", arguments=selections
        )

    config_text = render_template_custom(templatefile="base_config.json.j2", arguments=selections)

    logger.info(f"Writing config to `{config_path}`.")
    logger.info(
        "Please make sure to check the configuration contents and adjust settings to your needs."
    )

    config_path.write_text(config_text)

def start_new_config(args: dict[str, any]) -> None:
    """
    Create a new strategy from a template
    """
    from freqtrade.configuration.deploy_config import (
        ask_user_overwrite,
    )
    from freqtrade.configuration.directory_operations import chown_user_directory

    pair_path = Path(args["pair_config"])
    deploy_new_pairs(pair_path, args.get("pairs", []))

    config_path = Path(args["config"][0])
    chown_user_directory(config_path.parent)
    if config_path.exists():
        overwrite = args.get("overwrite", True)
        if overwrite:
            overwrite = args.get("overwrite", ask_user_overwrite(config_path))
        if overwrite:
            config_path.unlink()
        else:
            logger.warning(
                f"Configuration file `{config_path}` already exists. "
            )
            return
    selections = default_config(args)
    deploy_new_config(config_path, selections)