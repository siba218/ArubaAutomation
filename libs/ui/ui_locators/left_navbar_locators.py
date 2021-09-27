from selenium.webdriver.common.by import By


class LeftNavbarLocators:
    LABEL_OVERVIEW = (By.CSS_SELECTOR, "#global_overview")
    LABEL_DEVICES = (By.CSS_SELECTOR, "#global_infrastructure")
    LABEL_CLIENTS = (By.CSS_SELECTOR, "#global_clients")
    LABEL_GUESTS = (By.CSS_SELECTOR, "#global_guests")
    LABEL_APPLICATIONS = (By.CSS_SELECTOR, "#global_applications")
    LABEL_SECURITY = (By.CSS_SELECTOR, "#global_security")
    LABEL_NETWORK_SERVICES = (By.CSS_SELECTOR, "#global_network_services")
    LABEL_ALERTS_EVENTS = (By.CSS_SELECTOR, "#global_alerts_events")
    LABEL_AUDIT_TRAIL = (By.CSS_SELECTOR, "#global_audit_trail")
    LABEL_TOOLS = (By.CSS_SELECTOR, "#global_tools")
    LABEL_REPORTS = (By.CSS_SELECTOR, "#global_reports")
    LABEL_FIRMWARE = (By.CSS_SELECTOR, "#global_firmware")
    LABEL_ORGANIZATION = (By.CSS_SELECTOR, "#global_organization")