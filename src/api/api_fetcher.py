import httpx

class APIFetcher:
    def __init__(self, *, api_timeout: float = 10.0) -> None:
        self.api_timeout = api_timeout

    def fetch(self, request_url, api_parameters: dict = None) -> httpx.Response:
        """Fetches data from the API and returns it as a list of dictionaries.

        Args:
            request_url (str): The URL to which the API request will be sent.
            api_parameters (dict, optional): A dictionary of parameters to be sent with the API request. Defaults to None.
        """
        response = httpx.get(request_url, params=api_parameters, timeout=self.api_timeout)
        # TODO: Consider adding error handling for non-200 status codes, such as logging the error or raising an exception.
        # response.raise_for_status()  # Raise an exception for HTTP errors

        return response
