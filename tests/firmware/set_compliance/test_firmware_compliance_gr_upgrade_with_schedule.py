import sys
import time

from libs.api.FirmwareServices.firmware_request_builders import FirmwareComplianceRequestBuilder
from libs.utils.TimeUtils import TimeUtils
from tests.firmware.base_firmware_test import FirmwareTestBase
from tests.firmware.firmware_constants import FirmwareConstants


class FirmwareComplianceGrUpgrareScheduleTests(FirmwareTestBase):
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

    def test_upgrade_a_group_with_set_compliance_and_scheduling(self):
        epoch_time_2_min_ahead = TimeUtils().get_current_epoc_time(2, convert_mili=False)
        payload = FirmwareComplianceRequestBuilder()\
            .with_set_firmware_compliance({"HPPC": self.to_firmware_version}) \
            .with_compliance_scheduled_at(epoch_time_2_min_ahead) \
            .with_timezone("+05:30")\
            .with_groups([self.group_id])\
            .build()

        # self.firmware_obj.set_group_compliance_check(data=payload)
        self.firmware_obj.set_group_compliance(data=payload)

        self.log.printLog("wait for 2 mins as firmware upgrade has been scheduled after two mins of current time..")
        time.sleep(120)

        self.log.printLog("payload is: {}".format(payload))
        if self.wait_for_device_reboot(self.device_serial):
            self.log.printLog("Upgrade is complete")
            self.log.printLog("verifying Upgraded firmware version..")
            self.assertEqual(self.to_firmware_version, self.get_device_firmware_vesion(self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    def tearDown(self):
        # turn off set compliance for the same group
        payload = FirmwareComplianceRequestBuilder() \
            .with_groups([self.group_id]) \
            .with_delete_firmware_compliance({"CX": "none", "HPPC": "none"}) \
            .build()
        self.firmware_obj.set_group_compliance(data=payload)

    @classmethod
    def tearDownClass(cls):
        cls.session.disconnect()
