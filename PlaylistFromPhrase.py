import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
from requests import post, get
import json
import config

# Client side codes necessary to access API
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET