"""
Author       : ChenKailun
Date         : 2021-04-25 20:59
LastEditTime : 2021-04-25 23:32
FilePath     : /license_control/core/config.py
Description  :
"""

from Crypto.Cipher import AES


class Config:
    seperate_key: str = "qD#z34:IwT"  # 随机分隔字符串
    aes_key: str = "yujnye51qllq7z3g"  # 加密与解密所使用的密钥，长度必须是16的倍数
    aes_iv: str = "030cszkecj8qk11l"  # initial Vector, 长度要与aes_key一致
    aes_mode = AES.MODE_CBC
