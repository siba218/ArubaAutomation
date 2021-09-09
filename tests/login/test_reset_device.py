from unittest import TestCase

from libs.utils.customer_logger import CustomLogger
from rest.RestFrontEnd import RestFrontEnd



class LoginTest(TestCase):

    @classmethod
    def setUpClass(cls):
        sess = RestFrontEnd(host="https://app-yoda.arubathena.com",
                            user="smohanta32+23@gmail.com",
                            password="Aruba$123", customer_id="09ac85f3c5484e8683a31a86554de96f")

    def setUp(self):
        CustomLogger.setup_logger()
        log = CustomLogger()

    def test_sample_user_login(self):
        sess = RestFrontEnd(host="https://app-yoda.arubathena.com",
                            user="smohanta32+23@gmail.com",
                            password="Aruba$123", customer_id="09ac85f3c5484e8683a31a86554de96f")
        # sess.get(sess.host+"monitor/v2/switches",params={"status":"down"})
