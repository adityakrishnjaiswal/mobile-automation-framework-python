"""Login screen page object."""

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Encapsulates login flow interactions and locator fallbacks."""

    # Primary locators
    agree_terms = (By.ID, "agree_terms_btn")
    get_started = (By.ID, "get_started_btn")
    email_field = (By.ID, "email_field")
    next_button = (By.ID, "next_btn")
    password_field = (By.ID, "password_field")
    sign_in = (By.ID, "sign_in_btn")
    chat_tab = (By.ID, "chat_tab")

    # Example alternates for fallback
    chat_tab_alternates = [
        {"by": By.XPATH, "value": "//android.widget.TextView[@text='Chat']"},
        {"by": AppiumBy.ACCESSIBILITY_ID, "value": "Chat"},
    ]

    def login(self, username: str, password: str):
        """Complete the happy-path login sequence."""
        self.click(self.agree_terms)
        self.click(self.get_started)
        self.type(self.email_field, username)
        self.click(self.next_button)
        self.type(self.password_field, password)
        self.click(self.sign_in)
        return self

    def is_logged_in(self) -> bool:
        """Best-effort check that user reached chat tab."""
        return self.is_visible(self.chat_tab) or bool(self.find(self.chat_tab, self.chat_tab_alternates))


__all__ = ["LoginPage"]
