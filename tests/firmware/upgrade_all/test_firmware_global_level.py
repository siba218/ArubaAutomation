import sys

from tests.firmware.base_firmware_test import FirmwareTestBase
from tests.firmware.firmware_constants import FirmwareConstants


class FirmwareTests(FirmwareTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_file_name = __file__
        cls.device_serial_from_config = cls.aruba_automation_config.get_property('TestCase', cls.current_file_name)
        cls.device_serial = cls.device_serial_from_config.split("_")[1]
        cls.log.printLog("device serial assigned for the test is :{}".format(cls.device_serial))

    def setUp(self):
        self.log.printLog("Verifying device is online in setup....")
        self.status, self.site_id, self.group_id, self.version = self.get_device_status_site_group_ids_and_version(
            self.device_serial)
        if self.status == 1:
            self.log.printLog("Device is onilne . Progressing  with test...")
        else:
            self.log.printLog("device is offline...")
            self.log.printLog("exiting from test")
            sys.exit(1)

    def test_upgrade_all_device_of_individual_site(self):
        """
        payload = {"reboot":true,"when":0,"timezone":"+00:00","partition":"primary","sites":{"1":"16.10.0016"},"devices":{}}
        """
        if self.version == FirmwareConstants.SWITCH_RECOMMENDED_VERSION:
            payload = {"reboot": True, "when": 0, "timezone": "+00:00", "partition": "primary",
                       "sites": {self.site_id: FirmwareConstants.SWITCH_VERSION_15}, "devices": {}}
        elif self.version == FirmwareConstants.SWITCH_VERSION_15:
            payload = {"reboot": True, "when": 0, "timezone": "+00:00", "partition": "primary",
                       "sites": {self.site_id: FirmwareConstants.SWITCH_VERSION_14}, "devices": {}}
        else:
            payload = {"reboot": True, "when": 0, "timezone": "+00:00", "partition": "primary",
                       "sites": {self.site_id: FirmwareConstants.SWITCH_RECOMMENDED_VERSION}, "devices": {}}

        self.firmware_obj.upgrade_all(data=payload)

        if self.wait_for_device_grade(self.device_serial):
            self.log.printLog("Upgrade is complete")
            self.log.printLog("verifying Upgraded firmware version..")
            self.assertEqual(payload["sites"][self.site_id], self.get_device_firmware_vesion(self.device_serial))
        else:
            self.fail("device get stuck during firmware upgrade")
