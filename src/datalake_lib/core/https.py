import requests

class ExternalRequestError(RuntimeError):
    def __init__(self,message:str,*,retryable:bool):
        super().__init__(message)
        self.retryable = retryable

HTTP_ERROR_MAP = {
    400: ("Bad request to upstream", False),
    401: ("Unauthorized", False),
    403: ("Forbidden", False),
    404: ("Not found", False),
    429: ("Rate limited", True),
    500: ("Upstream server error", True),
    502: ("Bad gateway", True),
    503: ("Service unavailable", True),
    504: ("Gateway timeout", True),
}

def _handle_http_error(status_code:int)-> None:
    message,retryable = HTTP_ERROR_MAP.get(status_code,f"Unexpeced HTTP status: {status_code}",True)
    raise ExternalRequestError(message=message,retryable=True)
    

def external_data_fetch(*,url:str,header: dict, params:dict):
    try:
        response = requests.get(url,headers=header, params={"api_key": params},timeout=30)
    except requests.Timeout as e:
        raise ExternalRequestError(message="Network timeout",retryable=True) from e

    except requests.ConnectionError as e:
        raise  ExternalRequestError(message="Connect failure",retryable=True) from e

    except requests.RequestException as e:
        raise ExternalRequestError(message="Unexpected Failure",retryable=True) from e

    status_code = response.status_code()

    if status_code > 400:
        _handle_http_error(status_code=status_code)
    
    return response
        





def external_data_stream(*,url:str,header:dict,params:dict):
    pass
