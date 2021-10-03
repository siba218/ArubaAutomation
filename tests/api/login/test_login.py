import time
from unittest import TestCase

from libs.api.FirmwareServices.firmware_api import FirmwareApi
from libs.utils.aruba_automation_config import ArubaAutomationConfig
from libs.utils.customer_logger import CustomLogger
from libs.utils.RestFrontEnd import RestFrontEnd
from tests.api.login.base_user_login_test import UserLoginTestBase


class LoginTest(UserLoginTestBase):

    @classmethod
    def setUpClass(cls):
        super(LoginTest, cls).setUpClass()
        cls.email = cls.aruba_automation_config.get_property("user", "email")
        cls.password = cls.aruba_automation_config.get_property("user", "password")
        cls.login_url = cls.aruba_automation_config.get_property("central", "login_url")
        cls.customer_id = cls.aruba_automation_config.get_property("user", "customer_id")
        cls.session = RestFrontEnd(host=cls.login_url, user=cls.email, password=cls.password,
                                   customer_id=cls.customer_id)

    def setUp(self):

        self.payload = {
            "name": "testing2",
            "set_as_prefered_settings": False,
            "mixed_template_type": {
                "IAP": False,
                "MC": False,
                "SWITCH": False,
                "CX": False
            },
            "properties": {
                "DEVICE_TYPES": [
                    "AP",
                    "GW",
                    "SWITCHES"
                ],
                "ARCHITECTURE": "INSTANT",
                "AP_NETWORK_ROLE": "STANDARD",
                "GW_NETWORK_ROLE": "BGW",
                "ALLOWED_SW": [
                    "AOS_S",
                    "AOS_CX"
                ],
                "MONITOR_ONLY": [

                ]
            }
        }

    # testing  a GET call
    def test_get_devices_down_status(self):
        # print("RestFront end  object: {}".format(sess.__dict__))
        # print("session object: {}".format(sess.session.__dict__))
        # print("logger object : {}".format(sess.logger.__dict__))
        # sess.session.post()
        firmware = FirmwareApi()
        time.sleep(5)
        resp = firmware.get_devices_down_status(self.session, params={"status": "down"})
        self.assertEqual(resp.status_code, 200)
        # resp = self.session.get(self.session.host + "monitor/v2/switches", params={"status": "down"})
        # self.assertEqual(resp.status_code, 200)

    # testing a POST call
    def test_create_group(self):
        firmware = FirmwareApi()
        resp = firmware.create_group(self.session, data=self.payload)
        # resp = self.session.post(self.session.host + "groups/v2", data=self.payload)
        self.assertEqual(resp.status_code, 200)
        time.sleep(5)
        group_id = resp.body["group_id"]

        # testing a DELETE call
        resp1 = firmware.delete_group(self.session, group_id)
        self.assertEqual(resp1.status_code, 200)
