from selenium.webdriver.common.by import By


class LoginPageLocators:
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "#SignIn")
    EMAIL_FIELD = (By.CSS_SELECTOR, "#email")
    PASSWORD_FIELD = (By.CSS_SELECTOR, "#password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "#signIn_button")
