from selenium.webdriver.common.by import By


class OverviewPageLocators:
    AVATAR_BUTTON = (By.CSS_SELECTOR, "#LoginUserName")
    LOGOUT_LABEL = (By.CSS_SELECTOR, "#account_logout")
    WELCOME_POPUP_CLOSE = (By.CSS_SELECTOR, "#welcome_cloud_close_div")
