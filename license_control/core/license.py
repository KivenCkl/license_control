"""
Author       : ChenKailun
Date         : 2021-04-25 21:00
LastEditTime : 2021-04-28 20:58
FilePath     : /license_control/core/license.py
Description  :
"""
import hashlib
import uuid
from binascii import a2b_hex, b2a_hex
from datetime import datetime

from Crypto.Cipher import AES

from .config import Config


class License:
    def __init__(self, product_name: str):
        self.product_name = product_name.upper()

    @staticmethod
    def get_mac_addr() -> str:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return "-".join([mac[e : e + 2] for e in range(0, 11, 2)]).upper()

    @staticmethod
    def hash_msg(msg: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(msg.encode("utf-8"))

        return sha256.hexdigest()

    def create_pwd(self, mac_addr: str) -> str:
        return self.hash_msg(f"{self.product_name}{Config.seperate_key}{mac_addr}")

    @staticmethod
    def encrypt(msg: str) -> bytes:
        cryptor = AES.new(Config.aes_key, Config.aes_mode, Config.aes_iv)
        msg_b = msg.encode("utf-8")
        add, length = 0, 16
        count = len(msg_b)
        if (remain := count % length) != 0:
            add = length - remain

        msg_b += ("\0" * add).encode("utf-8")

        cipher_msg = cryptor.encrypt(msg_b)
        # 因为AES加密时得到的字符串不一定是ascii字符集，输出到终端或者保存时可能存在问题
        # 因此将加密后的字符串转化为16进制字符串
        return b2a_hex(cipher_msg)

    @staticmethod
    def decrypt(cipher_msg: bytes) -> str:
        cryptor = AES.new(Config.aes_key, Config.aes_mode, Config.aes_iv)
        msg = cryptor.decrypt(a2b_hex(cipher_msg))

        return bytes.decode(msg).rstrip("\0")

    def check_pwd(self, pwd: str) -> bool:
        mac_addr = self.get_mac_addr()

        hashed_msg = self.hash_msg(
            f"{self.product_name}{Config.seperate_key}{mac_addr}"
        )

        return hashed_msg == pwd

    @staticmethod
    def check_date(lic_date_str: str) -> bool:
        # current_time = datetime.now().isoformat()
        # current_time = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S.%f")
        current_time = datetime.now()
        lic_date = datetime.strptime(lic_date_str, "%Y-%m-%d %H:%M:%S")

        remain_days = (lic_date - current_time).days

        return remain_days >= 0
