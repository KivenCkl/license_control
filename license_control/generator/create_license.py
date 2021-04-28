"""
Author       : ChenKailun
Date         : 2021-04-24 19:02
LastEditTime : 2021-04-28 18:52
FilePath     : /license_control/generator/create_license.py
Description  :
"""
import json
import time
from pathlib import Path

from license_control.core.license import License
from PyQt5.QtCore import QDateTime, QStringListModel, Qt, QTimer
from PyQt5.QtWidgets import QDialog, QFileDialog

from .generator_ui import Ui_LicenseGeneratorDialog


class CreateLicense(QDialog, Ui_LicenseGeneratorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self._saved_dir = None
        self._mac_addrs = None
        self._key_state = False  # secret key is read only
        self.license_record = LicenseRecord()

        self._timer = parent.timer

        self.reset()
        self._configure_signals()

    def reset(self):
        self.now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.datetime_edit.setDateTime(
            QDateTime.fromString(self.now_time, "yyyy-MM-dd hh:mm:ss")
        )
        self._expire_date = self.datetime_edit.dateTime().toString(Qt.ISODate)
        self.mac_addr_text.setText("")
        self._mac_addrs = None

        items = self.license_record.get_license_history()
        list_model = QStringListModel()
        list_model.setStringList(items)
        self.record_list_view.setModel(list_model)

    def _configure_signals(self):
        self.saved_dir_button.clicked.connect(self.choose_saved_dir)
        self.change_state_button.clicked.connect(self.change_name_edit_state)
        self.datetime_edit.dateTimeChanged.connect(self.get_date)
        self.mac_addr_text.textChanged.connect(self.get_mac_addr)
        self.create_button.clicked.connect(self.generate_licenses)

        self._timer.timeout.connect(self.watch)

    def choose_saved_dir(self):
        self._saved_dir = QFileDialog.getExistingDirectory(self, "Choose Dir.", ".")
        self.saved_dir_line.setText(self._saved_dir)

    def change_name_edit_state(self):
        if not self._key_state:
            self.change_state_button.setText("Disable")
            self.product_name_line.setReadOnly(False)
        else:
            self.change_state_button.setText("Enable")
            self.product_name_line.setReadOnly(True)
        self._key_state = not self._key_state

    def watch(self):
        if self._saved_dir is None or self._mac_addrs is None:
            self.create_button.setEnabled(False)
        else:
            self.create_button.setEnabled(True)

    def get_date(self, dateTime=None):
        self._expire_date = dateTime.toString(Qt.ISODate)

    def get_mac_addr(self):
        addr = self.mac_addr_text.toPlainText().upper()
        self._mac_addrs = (
            mac for mac in map(lambda s: s.strip(), addr.split("\n")) if mac
        )

    def _generate_a_license(self, mac_addr: str):
        product_name = self.product_name_line.text().strip()
        license = License(product_name)
        psw = license.create_pwd(mac_addr)
        msg = json.dumps(dict(mac=mac_addr, time_str=self._expire_date, psw=psw))
        encrypt_msg = license.encrypt(msg)
        mac_str = mac_addr.replace("-", "")
        now_time_str = self.now_time.replace(" ", "_").replace(":", "")
        file_name = f"license_{mac_str}_{now_time_str}.lic"
        file_path = Path(self._saved_dir, file_name)
        file_path.write_bytes(encrypt_msg)

        record_msg = ",".join(
            [
                self.now_time,
                product_name,
                mac_str,
                self._expire_date,
                file_path.as_posix(),
            ]
        )
        self.license_record.write_license_record(record_msg)

    def generate_licenses(self):
        for mac_addr in self._mac_addrs:
            self._generate_a_license(mac_addr)

        self.reset()


class LicenseRecord:
    def __init__(self):
        self.record_file = Path("records.txt")

    def get_license_history(self) -> list[str]:
        try:
            with open(self.record_file, "r") as f:
                records = f.readlines()

            return records
        except FileNotFoundError:
            return []

    def write_license_record(self, records):
        with open(self.record_file, "a+") as f:
            if isinstance(records, list):
                records = "\n".join(records)
            f.write(records + "\n")
