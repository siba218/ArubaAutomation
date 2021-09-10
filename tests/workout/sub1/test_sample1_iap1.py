from libs.utils.file_utils import FileUtils
from tests.login.base_user_login_test import UserLoginTestBase


# below testcase is the example of how we are passing device serial to a testfile dynamically and not using any conftest.py file
# if use conftest then you can not debug in pycharm
# You can run your tests individually or file level as well

class SampleTestClass1(UserLoginTestBase):

    @classmethod
    def setUpClass(cls):
        super(SampleTestClass1, cls).setUpClass()
        cls.current_file_name = __file__.split('/')[-1]
        cls.device_serial_key = cls.aruba_automation_config.get_property('TestCase', cls.current_file_name)

    def setUp(self):
        device_mac = self.aruba_automation_config.get_property("SWITCH_" + self.device_serial_key, "mac_address")
        print("device mac address is: {}".format(device_mac))
        self.log.printStep("device serial key for the test : {}".format(self.device_serial_key))
        self.log.printLog("Starting {} test".format(self._testMethodName))
        print("device serial key :{}".format(self.device_serial_key))

        print(self.aruba_automation_config.get_sections())
        print(self.aruba_automation_config.get_switch_sections())

        self.aruba_automation_config.assign_switch_to_test_suites()

    def test_testing_command_line_arguments(self):
        self.log.printLog("inside test")
        print("fetching config values")
