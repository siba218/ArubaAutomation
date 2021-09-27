import time
from abc import abstractmethod

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from libs.utils.customer_logger import CustomLogger


class BasePage:
    """Base page object for common UI actions and element access."""

    def __init__(self, driver):
        self.driver = driver
        self.actions = ActionChains(driver)
        self._verify_page()
        self.log = CustomLogger()
        self.log.setup_logger()

    @abstractmethod
    def _verify_page(self):
        """  This method verifies that we are on the correct page. """
        return

    def enter_by_xpath(self, xpath, value):
        """ enter text to specified xpath """
        try:
            self.driver.find_element_by_xpath(xpath).send_keys(value)
        except NoSuchElementException as e:
            self.log.printDebug("ERROR " + e.msg)  # Log
            raise

    def enter_value_by_name(self, name, value):
        """ enter text by name """
        try:
            self.driver.find_element_by_name(name).send_keys(value)
        except NoSuchElementException as e:
            self.log.printDebug("ERROR " + e.msg)  # Log
            raise

    def enter_text(self, locator, text):
        """ general method to enter text by locator (from locators.py) - no need to specify locator type
            locator.__getitem__(0) - is locator type i.e. xpath , name , id
            locator.__getitem__(1) - is locator value based on locator type
        """
        try:
            self.driver.find_element(locator.__getitem__(0), locator.__getitem__(1)).click()
            self.driver.find_element(locator.__getitem__(0), locator.__getitem__(1)).clear()
            self.driver.find_element(locator.__getitem__(0), locator.__getitem__(1)).send_keys(text)
        except NoSuchElementException as e:
            self.log.printDebug("ERROR " + e.msg)  # Log
            raise

    def check_element_present(self, locator):
        """Check element is present or not.

        Args:
            locator: The locator tuple of the element.

        Returns:
            Return the element if the element is found, otherwise return false.

        locator.__getitem__(0) - is locator type i.e. xpath , name , id
        locator.__getitem__(1) - is locator value based on locator type

        """
        try:
            return self.driver.find_element(locator.__getitem__(0), locator.__getitem__(1))
        except NoSuchElementException as e:
            self.log.printDebug("ERROR " + e.msg)  # Log
            return False

    def is_element_present(self, locator):
        """ Check if element not present on page will not through NoSuchElementExceptions
            if element not present on page.
            custom method to check if buttons/element not present for staff roles

        Args:
            locator: The locator of the element.

        Returns:
            if elements don't exist return False, if exist, return the elements.

        """
        element = self.driver.find_elements(locator.__getitem__(0), locator.__getitem__(1))
        if len(element) == 0:
            return False
        else:
            return element

    def wait_for_element_not_present(self, wait_time, locator):
        WebDriverWait(self.driver, wait_time).until(
            EC.invisibility_of_element_located((locator.__getitem__(0), locator.__getitem__(1))))

    def wait_until_element_clickable(self, wait_time, locator_type, locator):
        """ Explicit wait for element with defined wait time """
        try:
            element = WebDriverWait(self.driver, wait_time). \
                until(EC.element_to_be_clickable((locator_type, locator)))
            return element
        except (NoSuchElementException, TimeoutException) as e:
            self.log.printDebug("ERROR " + e.msg)
            raise

    def click_button(self, wait_time, locator):
        """ allows to click any element - button or links """
        self.wait_for_element_visibility(wait_time, locator)
        self.wait_until_element_clickable(wait_time, locator.__getitem__(0), locator.__getitem__(1)).click()

    def click_element(self, wait_time, locator):
        """ allows to click any element """
        self.wait_for_element_visibility(wait_time, locator)
        self.wait_until_element_clickable(wait_time, locator.__getitem__(0), locator.__getitem__(1)).click()

    def click_button_with_sleep(self, wait_time, locator):
        """ allows to click any element - button or links """
        time.sleep(wait_time)
        self.wait_until_element_clickable(wait_time, locator.__getitem__(0), locator.__getitem__(1)).click()

    def get_text(self, locator):
        value = self.wait_for_element_visibility(10, locator).text
        return value

    def return_text_when_populated(self, locator, text_to_ignore, retry_count):
        for i in range(retry_count):
            self.wait(5)
            text = self.get_text(locator)
            if text == text_to_ignore:
                continue
            return text

    def get_value(self, locator):
        value = self.wait_for_element_visibility(10, locator).get_attribute('value')
        return str(value)

    def get_text_if_preset(self, locator):
        value = self.driver.find_element(locator.__getitem__(0), locator.__getitem__(1)).text
        return value

    def wait_for_element_visibility(self, wait_time, locator):
        """ Explicit wait for element till visible with defined wait time """
        while True:
            try:
                element = WebDriverWait(self.driver, wait_time). \
                    until(EC.visibility_of_element_located((locator.__getitem__(0), locator.__getitem__(1))))
                return element
            except(TimeoutError, NoSuchElementException) as e:
                print("ERROR " + e.msg)
                raise
            except StaleElementReferenceException:
                time.sleep(0.1)

    # Note: Another Idea, keeping here for reference
    # def _wait_for_element_visibility(self, wait_time, locator):
    #    """ Explicit wait for element till visible with defined wait time """
    #    WebDriverWait(self.driver, wait_time). \
    #                until(lambda s: s.find_element(locator.__getitem__(0), locator.__getitem__(1)).is_displayed())

    def find_one_element(self, locator):
        return self.driver.find_element(locator.__getitem__(0), locator.__getitem__(1))

    def find_all_elements(self, locator):
        return self.driver.find_elements(locator.__getitem__(0), locator.__getitem__(1))

    def check_dropdown(self, option_value_to_check, dropdown_locator_xpath=None, dropdown_css=None):
        if dropdown_locator_xpath:
            options_locator = (dropdown_locator_xpath[0], dropdown_locator_xpath[1] + "/option")
            options = self.find_all_elements(options_locator)
        elif dropdown_css:
            options = dropdown_css.find_elements_by_tag_name('option')
        for option in options:
            if option_value_to_check == option.text:
                return True
        return False

    def select_dropdown(self, locator, value):
        """ Allows selection of dropdown values  """
        try:
            dropdown = self.wait_for_element_visibility(2, locator)
            time.sleep(3)
            dropdown.click()
            time.sleep(1)
            Select(dropdown).select_by_visible_text(value)
        except NoSuchElementException as e:
            self.log.printDebug("ERROR: " + e.msg)
            raise

    def select_dropdown_scroll_to_visible(self, locator, scroll_to):
        """ Select dropdown value that is not visible on the screen """
        try:
            dropdown = self.wait_for_element_visibility(5, locator)
            dropdown.send_keys(scroll_to)
        except NoSuchElementException as e:
            print("ERROR: " + e.msg)
            raise

    def select_dropdown_without_click(self, locator, scroll_to):
        """ Select dropdown value that is not visible on the screen """
        try:
            dropdown = self.wait_for_element_visibility(2, locator)
            dropdown.send_keys(scroll_to)
        except NoSuchElementException as e:
            self.log.printDebug("ERROR: " + e.msg)
            raise

    def select_autocomplete_dropdwon(self, locator, value):
        """Select value from Auto Complete dropdown"""
        try:
            dropdown = self.wait_for_element_visibility(2, locator)
            dropdown.sendKeys(value, Keys.DOWN)
            dropdown.sendKeys(Keys.RETURN)
        except NoSuchElementException as e:
            print("ERROR: " + e.msg)
            raise

    def get_all_values_from_dropdown(self, locator):
        """
        :param locator:
        :return: all options
        """
        options_locator = (locator[0], locator[1] + "/option")
        options = self.find_all_elements(options_locator)
        return options

    def scroll_bottom_page(self):
        """ scrolling bottom of the page """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def wait(self, seconds):
        """ allows adding wait / sleep by seconds """
        time.sleep(seconds)

    def is_text_present(self, text):
        """ verify if passed text is present in page source """
        for i in range(5):
            page_source = self.driver.page_source
            if text in page_source:
                return True
            else:
                time.sleep(10)
                continue
        return False

    def select_checkbox(self, locator):
        """ allows select / unselect checkboxes """
        try:
            checkbox = self.wait_until_element_clickable(2, locator.__getitem__(0), locator.__getitem__(1))
            if checkbox.is_selected():
                print("deselecting checkbox")
                checkbox.click()
            else:
                print("selecting checkbox")
                checkbox.click()
        except NoSuchElementException as e:
            self.log.printDebug("ERROR: " + e.msg)
            raise

    def check_error_message_present(self):
        """ This method will check flash error message and return element if present else return None """
        try:
            element = self.driver.find_element_by_xpath("//div[@class='flash-message error']")
            return element
        except NoSuchElementException as e:
            self.log.printDebug("ERROR: " + e.msg)
            return None

    def verify_flash_message_content(self, locator, message):
        self.wait_for_element_visibility(10, locator)
        if self.get_text(locator) == message:
            return True
        return False

    def move_to_element(self, locator):
        try:
            el = self.find_one_element(locator)
            self.driver.execute_script("arguments[0].scrollIntoView();", el)
            time.sleep(2)
        except NoSuchElementException as e:
            self.log.printDebug("ERROR " + e.msg)  # Log
            raise

    def send_keys(self, locator, key):
        self.actions.send_keys_to_element(locator, getattr(Keys, "{}".format(key)))

    def mouse_click_element(self, web_element):
        """
        Click on an element using mouse actions.
        Use when getting this error when using click():
        "Element is not clickable at point (411, 675). Other element would receive the click" error
        Takes: webelement (Selenium)
        """
        self.actions.move_to_element(web_element).click().perform()

    def click_on_text(self, text):
        """
        Find link for specified text and Click on link
        :param text: pass text
        :return:
        """
        self.driver.find_element_by_link_text(text).click()

    def blur_active_element(self):
        """Blur the active element."""
        self.driver.execute_script('document.activeElement.blur()')

    def get_variables_from_table(self, table, num_col):
        """
        Get Text from a table columns
        Takes: table webelement, num_tables
                num_tables is a total number of colums in the table
        Returns: a dictionary
        Example: {'02/22/2017 at 5:04:02': 'Offline', '02/22/2017 at 5:04:03': 'Online', '02/22/2017 at 5:03:36': 'Initializing'}
        """

        def _grouped(iterable, n):
            return zip(*[iter(iterable)] * n)

        items = []
        final = {}
        try:
            self.wait_for_element_visibility(5, table)
            table = self.driver.find_element(table.__getitem__(0), table.__getitem__(1))
            for column in table.find_elements(By.TAG_NAME, "td"):
                items.append(column.text)
            print(items)
            if num_col == 2:
                for x, y in _grouped(items, num_col):
                    final[x] = y
                return final
            if num_col == 5:
                for x, y, z, q, w in _grouped(items, num_col):
                    final[x] = (y, z, q, w)
                return final
            if num_col == 6:
                for x, y, z, q, w, i in _grouped(items, num_col):
                    final[x] = (y, z, q, w, i)
                return final

        except NoSuchElementException as e:
            return False

    def get_element_class(self, locator):
        """
        Gets element's class
        """
        element = self.wait_for_element_visibility(5, locator=locator)
        return element.get_attribute("class")

    def send_upload_link(self, locator, file_path):
        """ Send file path to the choose file input field."""
        input_el = self.find_one_element(locator)
        input_el.send_keys(file_path)
        time.sleep(5)

    # not working properly
    # def wait_until_page_loads(self, max_wait=3000):
    #     counter = 0
    #     while counter < max_wait:
    #         state = self.driver.execute_script("return document.readyState")
    #         if state == "complete":
    #             return True
    #         time.sleep(5)
    #         counter = counter + 5
    #     return False


class IncorrectPageException(Exception):
    """This exception is raised when we try to instantiate the wrong page."""
    pass
