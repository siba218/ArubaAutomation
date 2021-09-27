from selenium.webdriver.common.by import By


class LoginPageLocators:
    BUTTON_CONTINUE = (By.CSS_SELECTOR, "#SignIn")
    EDITBOX_EMAIL = (By.CSS_SELECTOR, "#email")
    EDITBOX_PASSWORD = (By.CSS_SELECTOR, "#password")
    BUTTON_LOGIN = (By.CSS_SELECTOR, "#signIn_button")
