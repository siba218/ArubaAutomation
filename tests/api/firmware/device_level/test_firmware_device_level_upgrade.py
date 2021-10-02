import sys

from libs.api.FirmwareServices.firmware_request_builders import FirmwareDeviceRequestBuilder
from libs.utils.RestFrontEnd import RestFrontEnd
from tests.api.firmware.base_firmware_test import FirmwareTestBase
from tests.api.firmware.firmware_constants import FirmwareConstants


class FirmwareDeviceUpgradeTests(FirmwareTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.email = cls.aruba_automation_config.get_property("user", "email")
        cls.password = cls.aruba_automation_config.get_property("user", "password")
        cls.login_url = cls.aruba_automation_config.get_property("central", "login_url")
        cls.customer_id = cls.aruba_automation_config.get_property("user", "customer_id")
        cls.session = RestFrontEnd(host=cls.login_url, user=cls.email, password=cls.password,
                                   customer_id=cls.customer_id)
        cls.current_file_name = __file__
        cls.device_serial_from_config = cls.aruba_automation_config.get_property('TestCase', cls.current_file_name)
        cls.device_serial = cls.device_serial_from_config.split("_")[-1]
        cls.log.printLog("device serial assigned for the test is :{}".format(cls.device_serial))

    def setUp(self):
        self.log.printLog("Verifying device is online in setup....")
        self.status, self.site_id, self.group_id, self.version = self.get_device_status_site_group_ids_and_version(
            self.session,
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

    def test_upgrade_a_device(self):
        payload = FirmwareDeviceRequestBuilder().with_devices({self.device_serial: self.to_firmware_version}).build()

        self.firmware.upgrade_all(self.session, data=payload)

        self.log.printLog("payload is: {}".format(payload))
        if self.wait_for_device_reboot(self.session, self.device_serial):
            self.log.printLog("Upgrade is complete")
            self.log.printLog("verifying Upgraded firmware version..")
            self.assertEqual(self.to_firmware_version,
                             self.get_device_firmware_vesion(self.session, self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    def test_upgrade_a_device_with_reboot_later(self):
        payload = FirmwareDeviceRequestBuilder() \
            .with_devices({self.device_serial: self.to_firmware_version}) \
            .with_reboot(False) \
            .build()

        self.firmware.upgrade_all(self.session, data=payload)

        self.log.printLog("payload is: {}".format(payload))
        if self.wait_for_device_firmware_download(self.session, self.device_serial):
            self.log.printLog("Device firmware download complete")
            self.log.printLog("rebooting the device....")
            self.firmware.device_reboot(self.session, data={"device_id": self.device_serial})
            if self.wait_for_device_reboot(self.session, self.device_serial):
                self.assertEqual(self.to_firmware_version,
                                 self.get_device_firmware_vesion(self.session, self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    def test_upgrade_a_device_with_recommended_version(self):
        if self.version == FirmwareConstants.SWITCH_RECOMMENDED_VERSION:
            self.log.printLog("device already in recommended version")
            self.log.printLog("Downgrading device to some lower version..")
            payload = FirmwareDeviceRequestBuilder().with_devices(
                {self.device_serial: FirmwareConstants.SWITCH_VERSION_14}).build()
            self.firmware.upgrade_all(self.session, data=payload)

        new_payload = FirmwareDeviceRequestBuilder().with_devices({self.device_serial: None}).build()
        self.firmware.upgrade_all(self.session, data=new_payload)
        if self.wait_for_device_reboot(self.session, self.device_serial):
            self.log.printLog("Upgrade is complete")
            self.log.printLog("verifying Upgraded firmware version..")
            self.assertEqual(FirmwareConstants.SWITCH_RECOMMENDED_VERSION,
                             self.get_device_firmware_vesion(self.session, self.device_serial))
        else:
            self.fail("Firmware Upgrade Failed: device get stuck during firmware upgrade")

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.session.disconnect()
