from libs.ui.page_objects.central.left_navbar_page import LeftNavbarPage
from libs.ui.page_objects.central.login_page import LoginPage
from tests.base_universal_test import BaseUniversalTest


class LoginTest(BaseUniversalTest):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.browser = self.central_site_setup()
        self.login_page = LoginPage(self.browser)
        self.left_navbar_page = LeftNavbarPage(self.browser)



    def test_login(self):
        self.login_page.user_login("siba218@gmail.com", "Aruba@123")
        self.left_navbar_page.click_on_devices()
        self.left_navbar_page.click_on_overview()
        self.left_navbar_page.click_on_clients()
        self.left_navbar_page.click_on_guests()
        self.left_navbar_page.click_on_applications()
        self.left_navbar_page.click_on_security()
        self.left_navbar_page.click_on_network_services()
        self.left_navbar_page.click_on_alerts_and_events()
        self.left_navbar_page.click_on_audit_trail()
        self.left_navbar_page.click_on_tools()
        self.left_navbar_page.click_on_reports()
        self.left_navbar_page.click_on_firmware()
        self.left_navbar_page.click_on_organization()

    def tearDown(self):
        self.browser.close()
        self.browser.quit()
