import google.auth
import google.oauth2.credentials


def authenticate():
    CLIENTSECRETS_LOCATION = 'C:\Users\amaan\OneDrive\Desktop\Personal\Projects\client_secret.json'
    REDIRECT_URI = 'http://localhost:8080/'

    SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
              'https://www.googleapis.com/auth/userinfo.profile']

    credentials = google.oauth2.credentials.Credentials('access_token')


authenticate()  # to run script if needed
