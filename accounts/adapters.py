from allauth.account.adapter import DefaultAccountAdapter
from allauth.account import app_settings
from allauth.utils import import_attribute


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = "https://bitgifty.com/auth/email-confirm/" + emailconfirmation.key
        return url

    def get_adapter(request=None):
        """
        The Adapter in app_settings.ADAPTER is set to CustomAccountAdapter.
        """
        return import_attribute(app_settings.ADAPTER)(request)

