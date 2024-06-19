from tls_client import Session
from loguru import logger
from requests import get
from web3 import Web3
from time import sleep

from settings import *

from tls_client.exceptions import TLSClientExeption


class Browser:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.session = self.get_new_session()
        self.session.headers.update({
            "Origin": None,
            "Referer": None,
        })

    def get_new_session(self):
        session = Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True
        )
        session.headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        if self.proxy:
            session.proxies.update({'http': self.proxy, 'https': self.proxy})

        return session

    def get_eligibility(self, address: str, retry: int = 0):
        try:
            r = self.session.get(f"https://www.layerzero.foundation/api/allocation/{address.lower()}")
            if r.json().get("error") == "Record not found":
                status = "Not Eligible"
                tokens = 0
            else:
                status = "Eligible" if r.json()["isEligible"] else "Not Eligible"
                tokens = float(r.json()["zroAllocation"]["asString"])

            if status == "Eligible":
                logger.success(f'[+] Browser | {address} ELIGIBLE | {tokens} $ZRO')
            else:
                logger.error(f'[+] Browser | {address} NOT ELIGIBLE')

            return status, tokens

        except Exception as err:
            logger.error(f"[-] Browser | Couldn't get eligibility: {err} [{retry + 1}/{RETRY}]")
            if retry < RETRY:
                sleep(3)
                return self.get_eligibility(address=address, retry=retry + 1)
            else:
                return "Couldn't get eligibility", 0
