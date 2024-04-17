import requests
from datetime import datetime, timezone
import os
import pandas as pd
import time

class EZEManager:
    """INITIAL SETUP"""
    def __init__(self):
        try:
            self.EZE_API_HOST = os.environ['EZE_API_HOST']
            self.EZE_API_PORT = os.environ['EZE_API_PORT']
            self.EZE_API_CLIENT_ID = os.environ['EZE_API_CLIENT_ID']
            self.EZE_API_CLIENT_SECRET = os.environ['EZE_API_CLIENT_SECRET']
            self.EZE_ACCESS_TOKEN = None
            self.EZE_ACCESS_TOKEN_EXPIRY = None
            self.EZE_ACCESS_TOKEN_ERROR = None
        except KeyError as e:
            raise KeyError(f"Missing environment variable: {e}")
        
    """A METHOD TO GET THE ACCESS TOKEN FROM THE API SO WE CAN CONNECT"""
    def get_token(self):
        # URI for token retrieval
        uri = f"https://{self.EZE_API_HOST}:{self.EZE_API_PORT}/api/v1/token"

        # Data payload for the POST request
        data = {
            'client_id': self.EZE_API_CLIENT_ID,
            'client_secret': self.EZE_API_CLIENT_SECRET
        }

        # Try to send a POST request to the server
        try:
            response = requests.post(uri, data=data, verify=False)
            response.raise_for_status()  # This will raise an error for non-200 responses
        except requests.RequestException as e:
            self.EZE_ACCESS_TOKEN_ERROR = str(e)

        # Parse the JSON response
        try:
            token_info = response.json()
            self.EZE_ACCESS_TOKEN = token_info.get('access_token', '')
            self.EZE_ACCESS_TOKEN_EXPIRY = token_info.get('expires_by', '')
        except ValueError:
            self.EZE_ACCESS_TOKEN_ERROR = "Couldn't turn response into json format"
        except KeyError:
            self.EZE_ACCESS_TOKEN_ERROR = "Response JSON format is incorrect or missing expected fields"
    
    """Check if the current token is valid based on expiry time."""
    def check_token_validity(self):
        from datetime import datetime, timezone
        if self.EZE_ACCESS_TOKEN_EXPIRY is None:
            return False
        expiry_time = datetime.strptime(self.EZE_ACCESS_TOKEN_EXPIRY, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        return current_time < expiry_time
    
    """ANALYTICS API CALLS"""
    def get_analytics(self, endpoint, columns=None):
        if not self.check_token_validity():
            self.get_token()
            if not self.EZE_ACCESS_TOKEN:
                return None, None, "Failed to obtain token"
        
        # Create url from host, port, and endpoint
        url = r"https://"+ self.EZE_API_HOST + ":" + self.EZE_API_PORT + r"/api/v1/analytics/?view=" + endpoint
        
        # Check if we need to add specific columns
        if not columns is None:
            additional_url = "&columns=" + ",".join(columns)
            url = url + additional_url
            
        print(url)
        # Define all the variables
        headers = {
            'access_token': self.EZE_ACCESS_TOKEN,
            'client_id': self.EZE_API_CLIENT_ID
        }
        error = None
        response = None
        output_data = None
        
        # Check if we can get a response
        data_received = 0
        trials = 0
        while data_received == 0 and trials < 3:
            trials = trials + 1
            try:
                response = requests.get(url, headers=headers, verify=False)
                if response.status_code == 429:
                    print("Too many requests, will try again in 30 seconds. Sleeping for 30 seconds. This is trial number: ", trials)
                    time.sleep(31)
                elif response.status_code == 200:
                    data_received = 1
            except Exception as E:
                error = E

        if response is None:
            return output_data, response, False
        
        # Check if status is valid
        try:
            if response.status_code != 200:
                error = f"Response status code is expected to be 200, it's {response.status_code}"
                return None, response, error
        except:
            error = "Couldn't access response status code"
            return None, None, error
        
        # Check if we can parse the response
        try:
            response_json = response.json()
        except:
            error = "Couldn't turn response into json format"
            return None, response, error
        
        # Check if we can get column names
        try:
            column_names = response_json['columnMetadata']
        except:
            error = "Couldn't find column metadata in response"
            return None, response, error
        
        # Check if there's response data   
        try:
            data = response_json['responseData']
        except:
            error = "Couldn't find response data"
            return None, response, error
        
        # Check if we can turn this into a dataframe
        try:
            df = pd.DataFrame(data, columns=column_names)
        except Exception as E:
            error = "Couldn't create dataframe"
            print(E)
            return None, response, error
        
        return df, response, error
    