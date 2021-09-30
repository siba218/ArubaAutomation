import os
import time
from unittest import TestCase

import allure
from allure_commons.types import AttachmentType
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

from libs.api.FirmwareServices.firmware_api import FirmwareApi
from libs.api.GroupManagementServices.group_management_api import GroupManagementApi
from libs.utils.RestFrontEnd import RestFrontEnd
from libs.utils.aruba_automation_config import ArubaAutomationConfig
from libs.utils.customer_logger import CustomLogger


class BaseUniversalTest(TestCase):

    @classmethod
    def setUpClass(cls):
        # super().setUpClass()
        # os.environ[
        #     "ARUBA_AUTOMATION_TESTCASE_PATH"] = "/Users/sibasishmohanta/Documents/Development/ArubaAutomation/tests"
        cls.log = CustomLogger()
        cls.log.setup_logger()
        cls.aruba_automation_config = ArubaAutomationConfig(dump_flag=True, quiet=False)
        # Setting up Driver instance

    def get_central_sign_in_url(self):
        return self.aruba_automation_config.get_property("central", "login_url")

    def central_site_setup(self):
        driver = self.setup_browser()
        time.sleep(2)
        driver.get(self.get_central_sign_in_url())
        return driver

    def get_driver(self, selenium_env, capabilities, command_executor, chrome_path=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        # fixing issue - WebDriverException: Message: unknown error: DevToolsActivePort file doesn't exist
        chrome_options.add_argument('--disable-dev-shm-usage')
        BROWSER_MAPPING = {
            "firefox": webdriver.Firefox,
            "chrome": webdriver.Chrome,
            "safari": webdriver.Safari,
            "remote": webdriver.Remote
        }
        browser = capabilities.get("browserName")
        if selenium_env == 'remote':
            self.start = BROWSER_MAPPING[selenium_env](command_executor=command_executor,
                                                       desired_capabilities=capabilities,
                                                       options=chrome_options)
            return EventFiringWebDriver(self.start, ScreenshotListener())
        else:
            browser = BROWSER_MAPPING[browser](capabilities=capabilities) \
                if not chrome_path else BROWSER_MAPPING[browser](chrome_path)
            return browser

    def setup_browser(self):
        selenium_env = self.aruba_automation_config.get_property("BrowserSettings", "selenium_env")
        select_browser = self.aruba_automation_config.get_property("BrowserSettings", "browser_name")
        implicit_wait = self.aruba_automation_config.get_property("BrowserSettings", "implicit_wait")
        command_executor = self.aruba_automation_config.get_property("BrowserSettings", "selenium_hub")
        if select_browser == "firefox":
            firefox_capabilities = DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True
            self.driver = self.get_driver(selenium_env, firefox_capabilities, command_executor)
        elif select_browser == "chrome":
            chrome_capabilities = DesiredCapabilities.CHROME
            chrome_path = '{}/libs/browser/chromedriver'.format(
                os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
            self.driver = self.get_driver(selenium_env, chrome_capabilities, command_executor, chrome_path=chrome_path)
        else:
            raise Exception("Invalid browser selected - Supported browsers: Firefox, Chrome")
        self.driver.fullscreen_window()
        self.driver.implicitly_wait(implicit_wait)
        return self.driver

    @classmethod
    def tearDownClass(cls):
        cls.log.printLog("Inside Universal tearDownClass....")

    def tearDown(self):
        try:
            for method, err in self._outcome.errors:
                if err:
                    self.log.printLog("Test ended with an error. Taking screenshot")
                    allure.attach('test_error_screenshot', self.driver.get_screenshot_as_png(), type=AttachmentType.PNG)
            self.log.printLog('Test done - shutting down the browser')
            self.driver.close()
            self.driver.quit()
        except:
            self.log.printLog("Driver is already closed")


class ScreenshotListener(AbstractEventListener):
    """Listener for taking screenshot."""

    def on_exception(cls, exception, driver):
        """Take screenshot when the exception doesn't relate to stale element."""
        msg = "The element reference is stale. Either the element is no longer attached to the DOM or the page has" + \
              " been refreshed."
        if msg in exception.msg:
            print("Passing StaleElementReferenceException")
        else:
            allure.attach('exception_screenshot', driver.get_screenshot_as_png(), type=AttachmentType.PNG)
            driver.quit()
