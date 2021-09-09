from rest.RestFrontEnd import RestFrontEnd
from tests.base_universal_test import BaseUniversalTest
from utils.aruba_automation_config import ArubaAutomationConfig
from utils.customer_logger import CustomLogger
from utils.ping_utils import PingUtil


class ForceConnectDevice(BaseUniversalTest):
    def setUp(self):
        CustomLogger.setup_logger()
        log = CustomLogger()
        aruba_automation_config = ArubaAutomationConfig(dump_flag=True, quiet=False)
        self.email = aruba_automation_config.get_property("user", "email")
        self.password = aruba_automation_config.get_property("user", "password")
        self.login_url = aruba_automation_config.get_property("central", "login_url")
        self.customer_id = aruba_automation_config.get_property("user", "customer_id")
        self.force_connect_device_url = aruba_automation_config.get_property("device", "device_url") + "/ws"
        self.force_connect_commands = ['\n', "config terminal\n", "aruba-central url {}\n".format(self.force_connect_device_url),
                              "aruba-central enable\n", "exit\n", "show aruba-central\n"]

        self.log.printStep("Login User...........")
        self.sess = RestFrontEnd(host=self.login_url, user=self.email, password=self.password,
                                 customer_id=self.customer_id)

    def test_assign_license_and_force_connect(self):
        self.log.printStep("force connect device using SSHClient...........")
        PingUtil().ssh_device("10.22.108.82", "admin", "admin1234", self.force_connect_commands)
        PingUtil().ssh_device("10.21.31.166", "admin", "admin1234", self.force_connect_commands)

        self.log.printStep("Assigning license to the devices...........")



