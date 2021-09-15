import sys

from tests.firmware.base_firmware_test import FirmwareTestBase


class FirmwareTests(FirmwareTestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_file_name = __file__
        cls.device_serial_key = cls.aruba_automation_config.get_property('TestCase', cls.current_file_name)
        cls.log.printStep("device serial assigned for the test is :{}".format(cls.device_serial_key))
        cls.final_device_serial = cls.device_serial_key.split("_")[1]

    def setUp(self):
        self.log.printStep("Verifying device is online in setup....")
        device_status = self.get_device_status(self.final_device_serial)
        if device_status == 0:
            self.log.printStep("progress with test")
            self.log.printStep("test complete")
        else:
            self.log.printStep("device is offline...")
            self.log.printStep("exiting from test")
            sys.exit(1)

    def test_sample(self):
        pass
