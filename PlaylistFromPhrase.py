import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
from requests import post, get
import json
import config

# Client side codes necessary to access API
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET

# method to retrieve token from spotify api
def getToken():
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic" + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def getAuthHeader(token):
    return {"Authorization": "Bearer" + token}

def searchForSongs(token, input, offset):
    url = "https://api.spotify.com/v1/search"
    headers = getAuthHeader(token)
    query = f"?q={input}&type=track&market=US&limit=50&offset={offset}"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def cleanInput(inputStr):
    outputStr = ""
    for character in inputStr:
        if character.isalpha() or character.isspace():
            outputStr += character
        else:
            print("Please only use words and spaces, no punctuation or numbers.")
            exit()
    outputList = outputStr.split()
    return outputList
# temporary command line input

input = input("Please enter input: \n")

inputList = cleanInput(input)

trackList = []
token = getToken()
print("token: " + token)
for word in inputList:
    search = searchForSongs(token, word, 0)
    for item in search['tracks']['items']:
        if word.strip().lower() in item['name'].strip().lower():
            trackList.append(item)
            break
for item in trackList:
    print(f"\n{item['name']} by {item['artists'][0]['name']}")
