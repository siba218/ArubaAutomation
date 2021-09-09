from unittest import TestCase

from libs.utils.customer_logger import CustomLogger


class BaseUniversalTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = CustomLogger()
        cls.log.setup_logger()