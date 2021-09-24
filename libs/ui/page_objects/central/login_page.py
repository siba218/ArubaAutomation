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
        self.enter_text(LoginPageLocators.EMAIL_FIELD, username)
        self.click_element(10, LoginPageLocators.CONTINUE_BUTTON)
        self.wait_for_element_visibility(30, LoginPageLocators.PASSWORD_FIELD)
        self.enter_text(LoginPageLocators.PASSWORD_FIELD, password)
        self.click_element(10, LoginPageLocators.LOGIN_BUTTON)

        # Check for welcome popup
        self.wait_for_element_visibility(30, OverviewPageLocators.WELCOME_POPUP_CLOSE)
        element = self.check_element_present(OverviewPageLocators.WELCOME_POPUP_CLOSE)
        if element:
            self.log.printLog("Welcome PopUp found.. closing the popup")
            self.click_element(10, OverviewPageLocators.WELCOME_POPUP_CLOSE)
            self.wait_for_element_visibility(10, OverviewPageLocators.AVATAR_BUTTON)
            self.log.printLog("Login Complete")
