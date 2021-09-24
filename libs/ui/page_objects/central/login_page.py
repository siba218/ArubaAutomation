from libs.ui.page_objects.base_page import BasePage
from libs.ui.ui_locators.login_page_locators import LoginPageLocators


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
        
