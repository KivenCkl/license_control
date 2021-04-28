"""
Author       : ChenKailun
Date         : 2021-04-27 20:16
LastEditTime : 2021-04-28 18:51
FilePath     : /license_control/parser/check_license.py
Description  :
"""
import json
import shutil
from enum import Enum, auto
from pathlib import Path

from license_control.core.license import License
from PyQt5.QtWidgets import QDialog, QFileDialog

from .parser_ui import Ui_CheckLicenseDialog


class LicenseState(Enum):
    NotFound = auto()
    Inactive = auto()
    Active = auto()
    Expired = auto()


class CheckLicense(QDialog, Ui_CheckLicenseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.license = License(self.product_name_line.text().strip())
        self.mac_addr_label.setText(License.get_mac_addr())

        self._license_file = ""
        self.expire_date = ""
        self.psw = ""
        self.license_state = LicenseState.Inactive
        self.read_license()

        self._configure_signals()

    def _configure_signals(self):
        self.open_file_button.clicked.connect(self.choose_license_file)
        self.activate_button.clicked.connect(self.activate)
        self.close_button.clicked.connect(self.close)

    def choose_license_file(self):
        self._license_file, _ = QFileDialog.getOpenFileName(
            self, "Choose File", ".", "All Files (*.lic)"
        )
        self.license_file_line.setText(self._license_file)

    def activate(self):
        file = Path(self._license_file)
        if file.exists():
            try:
                path = shutil.copy(file, Path("license.lic"))
                self._license_file.setText(path)
            except Exception:
                pass
        self.read_license()

    def check_license_state(self):
        info = "<font color=#ff4757>Inactive</font>, Please activate software first!"
        if self.license_state == LicenseState.Active:
            info = f"<font color=#2ed573>Active</font>, Authorization deadline: {self.expire_date}"
        elif self.license_state == LicenseState.Expired:
            info = f"<font color=#ffa502>Expired</font>, Authorization deadline: {self.expire_date}"
        self.activation_state_label.setText(info)

    def read_license(self):
        license_file = Path("license.lic")
        if not license_file.exists():
            self.license_state = LicenseState.NotFound
        else:
            try:
                lic_msg = license_file.read_bytes()
                lic_str = License.decrypt(lic_msg)

                data = json.loads(lic_str)
            except Exception:
                data = {}
            self.expire_date = data.get("time_str", "").replace("T", " ")
            self.psw = data.get("psw", "")
            self.license_code_text.setText(self.psw)

            self.license_state = LicenseState.Inactive
            if self.expire_date and self.psw:
                check_date_result = License.check_date(self.expire_date)
                check_psw_result = self.license.check_pwd(self.psw)

                if check_psw_result:
                    if check_date_result:
                        self.license_state = LicenseState.Active
                    else:
                        self.license_state = LicenseState.Expired
        self.check_license_state()
