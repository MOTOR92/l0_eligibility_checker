from loguru import logger
from sys import stderr
from time import sleep
import random

import settings
from browser import Browser
from excel import Excel

logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{message}</level>")

def load_proxies(file_path: str):
    with open(file_path) as f:
        return f.read().splitlines()

def get_random_proxy(proxies: list):
    return random.choice(proxies) if proxies else None

def checker(address: str, excel: Excel, proxy: str = None):
    browser = Browser(proxy=proxy)
    status, tokens = browser.get_eligibility(address=address)

    excel.edit_table(wallet_data=[address, status, tokens])
    return {"status": status, "tokens": tokens}

if __name__ == "__main__":
    logger.info(f'LayerZero Checker\n')

    proxies = load_proxies('proxies.txt')
    if not proxies:
        logger.warning(f'No proxies loaded!\n')

    with open('addresses.txt') as f:
        addresses = f.read().splitlines()

    excel = Excel(total_len=len(addresses), name="l0_checker")

    total_tokens = 0
    total_eligibility = 0
    for address in addresses:
        proxy = get_random_proxy(proxies)
        result = checker(address=address, excel=excel, proxy=proxy)
        if result["status"] == "Eligible":
            total_eligibility += 1
            total_tokens += result["tokens"]

    eligible_percent = round(total_eligibility / len(addresses) * 100, 2)
    total_tokens = round(total_tokens, 2)

    excel.edit_table(wallet_data=[f"Total eligible addresses: [{total_eligibility}/{len(addresses)}]"])
    excel.edit_table(wallet_data=[f"Total tokens: {total_tokens} $ZRO"])

    print('\n')
    sleep(0.1)
    logger.success(f'Results saved in "results/{excel.file_name}"\n\nTotal eligibility: {eligible_percent}% [{total_eligibility}/{len(addresses)}] with {total_tokens} $ZRO\n\n')
    sleep(0.1)
    input('> Exit')
