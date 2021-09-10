from unittest import TestCase

from libs.utils.aruba_automation_config import ArubaAutomationConfig
from libs.utils.customer_logger import CustomLogger


class BaseUniversalTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = CustomLogger()
        cls.log.setup_logger()
        cls.aruba_automation_config = ArubaAutomationConfig(dump_flag=True, quiet=False)