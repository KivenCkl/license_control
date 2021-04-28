from license_control import __version__
from license_control.core.license import License


def test_version():
    assert __version__ == "0.1.0"


class TestLicense:
    def test_decrypt(self):
        license = License("test")
        msg = "test"
        assert license.decrypt(license.encrypt(msg)) == msg
