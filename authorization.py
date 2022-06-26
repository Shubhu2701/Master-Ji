import tekore as tk

def authorize():
    CLIENT_ID = '8493d46fcce94ddba94686f245d1a9f3'
    CLIENT_SECRET = '575abce2b48a4c3094ed0c2ca4888230'
    app_token = tk.request_client_token(CLIENT_ID, CLIENT_SECRET)
    return tk.Spotify(app_token)