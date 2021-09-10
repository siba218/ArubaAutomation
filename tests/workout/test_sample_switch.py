import configparser
import sys

from libs.utils.aruba_automation_config import ArubaAutomationConfig
from tests.login.base_user_login_test import UserLoginTestBase

# below testcase is the example of how we are passing device serial to a testfile dynamically and not using any conftest.py file
# if use conftest then you can not debug in pycharm
# You can run your tests individually or file level as well

class SampleTestClass(UserLoginTestBase):
    def setUp(self):
        self.aruba_automation_config = ArubaAutomationConfig(dump_flag=True, quiet=False)
        self.device_serial_key = self.aruba_automation_config.get_property('TestCase','new_test_key')
        self.log.printLog("Starting {} test".format(self._testMethodName))
        print("device serial key :{}".format(self.device_serial_key))

    def test_testing_command_line_arguments(self):
        self.log.printLog("inside test")
        print("fetching config values")

