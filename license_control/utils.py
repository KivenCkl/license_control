"""
Author       : ChenKailun
Date         : 2021-04-24 19:03
LastEditTime : 2021-04-24 19:12
FilePath     : /license_control/utils.py
Description  :
"""
import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource
    works for dev and for PyInstaller"""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)
