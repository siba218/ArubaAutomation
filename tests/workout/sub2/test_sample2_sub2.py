import configparser
import sys

from libs.utils.aruba_automation_config import ArubaAutomationConfig
from tests.login.base_user_login_test import UserLoginTestBase


# below testcase is the example of how we are passing device serial to a testfile dynamically and not using any conftest.py file
# if use conftest then you can not debug in pycharm
# You can run your tests individually or file level as well

class SampleTestClass2(UserLoginTestBase):
    @classmethod
    def setUpClass(cls):
        super(SampleTestClass2, cls).setUpClass()
        cls.current_file_name = __file__
        cls.device_serial_key = cls.aruba_automation_config.get_property('TestCase', cls.current_file_name)

    def setUp(self):
        self.log.printStep(
            "device serial key for the test- {} : {}".format(self._testMethodName, self.device_serial_key))
        self.log.printLog("Starting {} test".format(self._testMethodName))

    def test_sample2_gateways1_1(self):
        self.log.printLog("inside test")
        print("fetching config values")

    def test_sample2_gateways1_2(self):
        self.log.printLog("inside test")
        print("fetching config values")

