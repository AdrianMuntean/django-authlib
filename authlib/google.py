import os

from django.conf import settings

from requests_oauthlib import OAuth2Session


class GoogleOAuth2Client(object):
    authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://www.googleapis.com/oauth2/v4/token"
    scope = ["openid", "email", "profile"]
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET

    def __init__(self, request, *, login_hint=None):
        # let oauthlib be less strict on scope mismatch
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

        self._request = request
        self._session = OAuth2Session(
            self.client_id,
            scope=self.scope,
            redirect_uri=request.build_absolute_uri("."),
        )
        self._login_hint = login_hint

    def get_authentication_url(self):
        authorization_url, self._state = self._session.authorization_url(
            self.authorization_base_url, login_hint=self._login_hint
        )

        return authorization_url

    def get_user_data(self):
        self._session.fetch_token(
            self.token_url,
            client_secret=self.client_secret,
            authorization_response=self._request.build_absolute_uri(
                self._request.get_full_path()
            ),
        )
        data = self._session.get("https://www.googleapis.com/oauth2/v3/userinfo").json()

        return (
            {"email": data.get("email"), "full_name": data.get("name")}
            if data.get("email_verified")
            else {}
        )
