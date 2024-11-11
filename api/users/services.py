import requests


class SocialLoginService:
    def __init__(self, client_id, redirect_uri, login_uri):
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.login_uri = login_uri

    def social_login(self, context=None):
        if context is not None:
            return self.basic_url() + f"&scope={context['scope']}"

        return self.basic_url()

    def basic_url(self):
        return f"{self.login_uri}?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code"


class SocialLoginCallbackService:
    def __init__(self, client_id, client_secret, redirect_uri, token_uri, profile_uri):
        self.grant_type = "authorization_code"
        self.content_type = "application/json"
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_uri = token_uri
        self.profile_uri = profile_uri

    def create_token_request_data(self, code):
        token_request_data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        return token_request_data

    def get_access_token(self, token_request_data):
        token_response = requests.post(
            self.token_uri,
            data=token_request_data,
            headers={"Accept": self.content_type},
        )
        if token_response.status_code != 200:
            raise ValueError(token_response.text)

        token_json = token_response.json()
        access_token = token_json.get("access_token")

        return access_token

    def get_user_info(self, auth_headers):
        user_info_response = requests.get(self.profile_uri, headers=auth_headers)
        user_info_data = user_info_response.json()

        return user_info_data
