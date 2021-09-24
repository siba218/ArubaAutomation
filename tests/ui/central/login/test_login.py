from libs.ui.page_objects.central.login_page import LoginPage
from tests.base_universal_test import BaseUniversalTest


class LoginTest(BaseUniversalTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.browser = self.central_site_setup()
        self.login_page = LoginPage(self.browser)

    def test_login(self):
        self.login_page.user_login("siba218@gmail.com", "Aruba@123")

    def tearDown(self):
        self.browser.close()
        self.browser.quit()
