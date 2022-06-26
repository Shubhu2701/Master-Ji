import tekore as tk
import os
from dotenv import load_dotenv

load_dotenv()
clientID=os.getenv('ID')
clientSecret=os.getenv('SECRET')

def authorize():
    app_token = tk.request_client_token(clientID, clientSecret)
    return tk.Spotify(app_token)