import time

from libs.api.FirmwareServices.firmware_api import FirmwareApi
from tests.base_universal_test import BaseUniversalTest


class FirmwareTestBase(BaseUniversalTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.firmware = FirmwareApi()

    def get_device_status_site_group_ids_and_version(self, session, device_serial):
        resp = self.firmware.get_switch_list_details(session)
        for item in resp.body["device_info"]:
            if item["device_id"] == device_serial:
                return [item["device_status"], item["site_id"], item["group_id"], item["version"]]

    def get_device_firmware_vesion(self, session, device_serial):
        resp = self.firmware.get_switch_list_details(session)
        for item in resp.body["device_info"]:
            if item["device_id"] == device_serial:
                return item["version"]

    def wait_for_device_reboot(self, session, device_serial, max_wait_time=300):
        count = 0
        status = ""
        self.log.printLog(
            "Waiting for the Firmware upgrade to complete. max time provided: {}sec".format(max_wait_time))
        while count < max_wait_time + 1:

            # wait for fw_staus=reboot to appear
            resp = self.firmware.get_switch_list_details(session)

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

    def wait_for_device_firmware_download(self, session, device_serial, max_wait_time=300):
        count = 0
        status = ""
        self.log.printLog(
            "Waiting for the Firmware upgrade to complete. max time provided: {}sec".format(max_wait_time))
        while count < max_wait_time + 1:

            # wait for fw_staus=reboot to appear
            resp = self.firmware.get_switch_list_details(session)

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
