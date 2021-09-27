import time

from libs.ui.page_objects.base_page import BasePage
from libs.ui.ui_locators.alerts_events_page_locators import AlertsEventsPageLocators
from libs.ui.ui_locators.applications_page_locators import ApplicationsPageLocators
from libs.ui.ui_locators.audit_trail_page_locators import AuditTrailPageLocators
from libs.ui.ui_locators.clients_page_locators import ClientsPageLocators
from libs.ui.ui_locators.device_page_locators import DevicesPageLocators
from libs.ui.ui_locators.firmware_page_locators import FirmwarePageLocators
from libs.ui.ui_locators.guests_page_locators import GuestPageLocators
from libs.ui.ui_locators.left_navbar_locators import LeftNavbarLocators
from libs.ui.ui_locators.network_services_page_locators import NetworksServicesPageLocators
from libs.ui.ui_locators.organization_page_locators import OrganizationsPageLocators
from libs.ui.ui_locators.overview_page_locators import OverviewPageLocators
from libs.ui.ui_locators.reports_page_locators import ReportsPageLocators
from libs.ui.ui_locators.security_page_locators import SecurityPageLocators
from libs.ui.ui_locators.tools_page_locators import ToolsPageLocators


class LeftNavbarPage(BasePage):
    def __init__(self, driver):
        self.sleep = 3
        super().__init__(driver)

    def _verify_page(self):
        pass

    def click_on_overview(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_OVERVIEW)
        self.click_element(30, LeftNavbarLocators.LABEL_OVERVIEW)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, OverviewPageLocators.TAB_SUMMARY)

    def click_on_devices(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_DEVICES)
        self.click_element(30, LeftNavbarLocators.LABEL_DEVICES)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, DevicesPageLocators.TAB_SWITCHES)

    def click_on_clients(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_CLIENTS)
        self.click_element(30, LeftNavbarLocators.LABEL_CLIENTS)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, ClientsPageLocators.TAB_CLIENTS)

    def click_on_guests(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_GUESTS)
        self.click_element(30, LeftNavbarLocators.LABEL_GUESTS)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, GuestPageLocators.TAB_GUEST_ACCESS)

    def click_on_applications(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_APPLICATIONS)
        self.click_element(30, LeftNavbarLocators.LABEL_APPLICATIONS)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, ApplicationsPageLocators.TAB_APPLICATIONS)

    def click_on_security(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_SECURITY)
        self.click_element(30, LeftNavbarLocators.LABEL_SECURITY)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, SecurityPageLocators.TAB_RAPID)

    def click_on_network_services(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_NETWORK_SERVICES)
        self.click_element(30, LeftNavbarLocators.LABEL_NETWORK_SERVICES)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, NetworksServicesPageLocators.TAB_SD_WAN_OVERLAY)

    def click_on_alerts_and_events(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_ALERTS_EVENTS)
        self.click_element(30, LeftNavbarLocators.LABEL_ALERTS_EVENTS)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, AlertsEventsPageLocators.TAB_ALERTS_AND_EVENTS)

    def click_on_audit_trail(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_AUDIT_TRAIL)
        self.click_element(30, LeftNavbarLocators.LABEL_AUDIT_TRAIL)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, AuditTrailPageLocators.TAB_AUDIT_TRAIL)

    def click_on_tools(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_TOOLS)
        self.click_element(30, LeftNavbarLocators.LABEL_TOOLS)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, ToolsPageLocators.TAB_NETWORK_CHECK)

    def click_on_reports(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_REPORTS)
        self.click_element(30, LeftNavbarLocators.LABEL_REPORTS)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, ReportsPageLocators.TAB_REPORTS)

    def click_on_firmware(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_FIRMWARE)
        self.click_element(30, LeftNavbarLocators.LABEL_FIRMWARE)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, FirmwarePageLocators.TAB_SWITCHES)

    def click_on_organization(self):
        self.wait_for_element_visibility(30, LeftNavbarLocators.LABEL_ORGANIZATION)
        self.click_element(30, LeftNavbarLocators.LABEL_ORGANIZATION)
        time.sleep(self.sleep)
        self.wait_for_element_visibility(30, OrganizationsPageLocators.TAB_NETWORK_STRUCTURE)
