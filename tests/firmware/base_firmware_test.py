from libs.api.FirmwareServices.firmware_api import FirmwareApi
from libs.utils import aruba_automation_config
from rest.RestFrontEnd import RestFrontEnd
from tests.base_universal_test import BaseUniversalTest


class FirmwareTestBase(BaseUniversalTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.email = cls.aruba_automation_config.get_property("user", "email")
        cls.password = cls.aruba_automation_config.get_property("user", "password")
        cls.login_url = cls.aruba_automation_config.get_property("central", "login_url")
        cls.customer_id = cls.aruba_automation_config.get_property("user", "customer_id")
        cls.session = RestFrontEnd(host=cls.login_url, user=cls.email, password=cls.password,
                                   customer_id=cls.customer_id)
        cls.firmware_obj = FirmwareApi(cls.session)
        cls.device_list_response = cls.firmware_obj.get_switch_list_details()

    def get_device_status(self, device_serial):
        for item in self.device_list_response.body["device_info"]:
            if item["device_id"] == device_serial:
                return item["device_status"]


