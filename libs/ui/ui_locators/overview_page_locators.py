from selenium.webdriver.common.by import By


class OverviewPageLocators:
    BUTTON_AVATAR = (By.CSS_SELECTOR, "#LoginUserName")
    LABEL_LOGOUT = (By.CSS_SELECTOR, "#account_logout")
    CLOSE_WELCOME_POPUP = (By.CSS_SELECTOR, "#welcome_cloud_close_div")
    TAB_SUMMARY = (By.CSS_SELECTOR, "#global_all_devices")
    BUTTON_SUMMARY_LIST = (By.CSS_SELECTOR, "#global_summary_list")
