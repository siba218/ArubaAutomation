import sys
import time

from nose_parameterized import parameterized

from libs.api.FirmwareServices.firmware_request_builders import FirmwareComplianceRequestBuilder
from tests.api.firmware.base_firmware_test import FirmwareTestBase
from tests.api.firmware.firmware_constants import FirmwareConstants


class FirmwareComplianceGrUpgrareTests(FirmwareTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_file_name = __file__
        cls.device_serial_from_config = cls.aruba_automation_config.get_property('TestCase', cls.current_file_name)
        cls.device_serial = cls.device_serial_from_config.split("_")[-1]
        cls.log.printLog("device serial assigned for the test is :{}".format(cls.device_serial))

    def setUp(self):
        self.log.printLog("Verifying device is online in setup....")
        self.status, self.site_id, self.group_id, self.version = self.get_device_status_site_group_ids_and_version(
            self.device_serial)
        if self.status == 1:
            self.log.printLog("Device is online . Progressing  with test...")
        else:
            self.log.printLog("device is offline...")
            self.log.printLog("exiting from test")
            sys.exit(1)

        # set firmware selection logic
        self.to_firmware_version = ""
        if self.version == FirmwareConstants.SWITCH_RECOMMENDED_VERSION:
            self.to_firmware_version = FirmwareConstants.SWITCH_VERSION_15
        elif self.version == FirmwareConstants.SWITCH_VERSION_15:
            self.to_firmware_version = FirmwareConstants.SWITCH_VERSION_14
        else:
            self.to_firmware_version = FirmwareConstants.SWITCH_RECOMMENDED_VERSION

        self.log.printLog("Upgraded firmware version for the test: {}".format(self.to_firmware_version))

    @parameterized.expand(
        [("primary",), ("secondary",),])
    def test_upgrade_a_group_with_set_compliance(self, partition):
        payload = FirmwareComplianceRequestBuilder()\
            .with_set_firmware_compliance({"HPPC":self.to_firmware_version})\
            .with_groups([self.group_id])\
            .with_partition(partition).\
            build()

        self.firmware.set_group_compliance(data=payload)

        self.log.printLog("payload is: {}".format(payload))
        if self.wait_for_device_reboot(self.device_serial):
            self.log.printLog("Upgrade is complete")
            self.log.printLog("verifying Upgraded firmware version..")
            self.assertEqual(self.to_firmware_version, self.get_device_firmware_vesion(self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    @parameterized.expand(
        [("primary",), ("secondary",),])
    def test_upgrade_a_group_with_set_compliance_and_reboot_later(self, partition):
        payload = FirmwareComplianceRequestBuilder() \
            .with_set_firmware_compliance({"HPPC": self.to_firmware_version}) \
            .with_groups([self.group_id]) \
            .with_reboot({"HPPC":False})\
            .with_partition(partition)\
            .build()

        self.firmware.set_group_compliance(data=payload)

        self.log.printLog("payload is: {}".format(payload))
        if self.wait_for_device_firmware_download(self.device_serial):
            self.log.printLog("Device firmware download complete")
            self.log.printLog("rebooting the device....")
            self.firmware.device_reboot(data={"device_id": self.device_serial})
            if self.wait_for_device_reboot(self.device_serial):
                self.assertEqual(self.to_firmware_version, self.get_device_firmware_vesion(self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    def tearDown(self):
        # turn off set compliance for the same group
        payload = FirmwareComplianceRequestBuilder() \
            .with_groups([self.group_id]) \
            .with_delete_firmware_compliance({"CX":"none","HPPC":"none"})\
            .build()
        self.firmware.set_group_compliance(data=payload)

    @classmethod
    def tearDownClass(cls):
        cls.session.disconnect()
