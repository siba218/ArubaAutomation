from libs.ui.page_objects.base_page import BasePage
from libs.ui.ui_locators.login_page_locators import LoginPageLocators
from libs.ui.ui_locators.overview_page_locators import OverviewPageLocators


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    def _verify_page(self):
        """Verify device page after login.

        Raises:
            IncorrectPageException: If list table and show per page button show up.

        """
        pass

    def user_login(self, username, password):
        self.enter_text(LoginPageLocators.EDITBOX_EMAIL, username)
        self.click_element(10, LoginPageLocators.BUTTON_CONTINUE)
        self.wait_for_element_visibility(30, LoginPageLocators.EDITBOX_PASSWORD)
        self.enter_text(LoginPageLocators.EDITBOX_PASSWORD, password)
        self.click_element(10, LoginPageLocators.BUTTON_LOGIN)

        # Check for welcome popup
        try:
            self.wait_for_element_visibility(30, OverviewPageLocators.CLOSE_WELCOME_POPUP)
            element = self.check_element_present(OverviewPageLocators.CLOSE_WELCOME_POPUP)
            if element:
                self.log.printLog("Welcome PopUp found.. closing the popup")
                self.click_element(10, OverviewPageLocators.CLOSE_WELCOME_POPUP)
                self.wait_for_element_visibility(10, OverviewPageLocators.BUTTON_AVATAR)
                self.log.printLog("Login Complete")
        except:
            self.log.printLog("Welcome popup not found after login with in 30 seconds.. Progressing with test.")
