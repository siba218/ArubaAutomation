import time

from libs.api.FirmwareServices.firmware_api import FirmwareApi
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

    def get_device_status_site_group_ids_and_version(self, device_serial):
        for item in self.device_list_response.body["device_info"]:
            if item["device_id"] == device_serial:
                return [item["device_status"], item["site_id"], item["group_id"], item["version"]]

    def get_device_firmware_vesion(self, device_serial):
        resp = self.firmware_obj.get_switch_list_details()
        for item in resp.body["device_info"]:
            if item["device_id"] == device_serial:
                return item["version"]

    def wait_for_device_reboot(self, device_serial, max_wait_time=300):
        count = 0
        status = ""
        self.log.printLog("Waiting for the Firmware upgrade to complete. max time provided: {}sec".format(max_wait_time))
        while count < max_wait_time + 1:

            # wait for fw_staus=reboot to appear
            resp = self.firmware_obj.get_switch_list_details()

            for item in resp.body["device_info"]:
                if item["device_id"] == device_serial:
                    status = item["fw_status"]

            if status != "reboot":
                self.log.printLog("status is not reboot.. waiting for next pool in 30sec for status to be reboot")
                time.sleep(30)
                count = count + 30
                self.log.printLog("total wait time in seconds : {}".format(count))
                try:
                    for item in resp.body["device_info"]:
                        if item["device_id"] == device_serial:
                            if item["status"]["status"] == "complete":
                                return True
                except:
                    pass
                continue

            # then wait for fw_staus=reboot to disappear
            if status == "reboot":
                self.log.printLog("status is reboot.. waiting for next pool in 30sec for reboot status to disappear")
                time.sleep(30)
                count = count + 30
                self.log.printLog("total wait time in seconds : {}".format(count))
        self.log.printLog("Max wait time is over. Device not upgraded")
        return False

    def wait_for_device_firmware_download(self, device_serial, max_wait_time=300):
        count = 0
        status = ""
        self.log.printLog("Waiting for the Firmware upgrade to complete. max time provided: {}sec".format(max_wait_time))
        while count < max_wait_time + 1:

            # wait for fw_staus=reboot to appear
            resp = self.firmware_obj.get_switch_list_details()

            for item in resp.body["device_info"]:
                if item["device_id"] == device_serial:
                    status = item["fw_status"]

            if status != "DOWNLOAD_COMPLETED":
                self.log.printLog("status is not DOWNLOAD_COMPLETED.. waiting for next pool in 30sec ")
                time.sleep(30)
                count = count + 30
                self.log.printLog("total wait time in seconds : {}".format(count))
                continue
            if status == "DOWNLOAD_COMPLETED":
                return True

        self.log.printLog("Max wait time is over. Device not upgraded")
        return False
