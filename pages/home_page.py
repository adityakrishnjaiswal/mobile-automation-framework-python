"""Home/landing page object."""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    chat_tab = (By.ID, "chat_tab")
    calls_tab = (By.ID, "calls_tab")
    activity_tab = (By.ID, "activity_tab")

    def open_calls(self):
        self.click(self.calls_tab)
        return self

    def open_chat(self):
        self.click(self.chat_tab)
        return self

    def open_activity(self):
        self.click(self.activity_tab)
        return self


__all__ = ["HomePage"]
