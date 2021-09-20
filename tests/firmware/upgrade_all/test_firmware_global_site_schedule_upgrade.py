import sys
import time

from libs.api.FirmwareServices.firmware_request_builders import FirmwareUpgradeRequestBuilder
from libs.utils.TimeUtils import TimeUtils
from tests.firmware.base_firmware_test import FirmwareTestBase
from tests.firmware.firmware_constants import FirmwareConstants


class FirmwareSiteUpgradeSchedulingTests(FirmwareTestBase):

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

        # set firmware selection logic
        self.to_firmware_version = ""
        if self.version == FirmwareConstants.SWITCH_RECOMMENDED_VERSION:
            self.to_firmware_version = FirmwareConstants.SWITCH_VERSION_15
        elif self.version == FirmwareConstants.SWITCH_VERSION_15:
            self.to_firmware_version = FirmwareConstants.SWITCH_VERSION_14
        else:
            self.to_firmware_version = FirmwareConstants.SWITCH_RECOMMENDED_VERSION

    def test_upgrade_all_device_of_site_with_device_local_and_scheduling(self):

        """
        This testcase is to upgrade all devices under a site with option : device local time + scheduling
         while upgrading using device_local_time you have to set timezone:"none"
         Steps:
            1. login with automation user and get the session object
            2. Verify the firmware available in the device and set the logic to upgrade the firmware
            3. Hit the firmware upgrade api with
                        1.site details
                        2. device local timestamp
                        3. Scheduling and wait for the upgrade to over
            4. Once Upgrade is over then verify the Upgraded software version in the device
         """
        epoch_time_2_min_ahead = TimeUtils().get_current_time_as_utc_in_epoch(2)
        payload = FirmwareUpgradeRequestBuilder(). \
            with_sites({self.site_id: self.to_firmware_version}) \
            .with_when(epoch_time_2_min_ahead) \
            .with_timezone("none").build()

        self.firmware_obj.upgrade_all(data=payload)

        self.log.printLog("wait for 2 mins as firmware upgrade has been scheduled after two mins of current time..")
        time.sleep(120)

        self.log.printLog("payload is: {}".format(payload))
        if self.wait_for_device_reboot(self.device_serial):
            self.log.printLog("Upgrade is complete")
            self.log.printLog("verifying Upgraded firmware version..")
            self.assertEqual(self.to_firmware_version, self.get_device_firmware_vesion(self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    def test_upgrade_all_device_of_individual_site_india_time_and_scheduling(self):

        """
        This testcase is to upgrade all devices under a site with option : with specific time zone + scheduling
        Steps:
            1. login with automation user and get the session object
            2. Verify the firmware available in the device and set the logic to upgrade the firmware
            3. Hit the firmware upgrade api
                        1.site details
                        2. select timezone as india - Asia/Kokata
                        3. Schedule and wait for the upgrade to over
            4. Once Upgrade is over then verify the Upgraded software version in the device
        """
        epoch_time_2_min_ahead = TimeUtils().get_current_epoc_time(2)
        payload = FirmwareUpgradeRequestBuilder(). \
            with_sites({self.site_id: self.to_firmware_version}) \
            .with_when(epoch_time_2_min_ahead) \
            .with_timezone("+05:30").build()

        self.firmware_obj.upgrade_all(data=payload)

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
        pass

    @classmethod
    def tearDownClass(cls):
        cls.session.disconnect()
