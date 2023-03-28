import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import base64
from requests import post, get
import json
import config
import PySimpleGUI as sg

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
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def getAuthHeader(token):
    return {"Authorization": "Bearer " + token}

def searchForSongs(token, input, offset):
    url = "https://api.spotify.com/v1/search"
    headers = getAuthHeader(token)
    query = f"?q={input}&type=track&market=US&limit=5&offset={offset}"
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

def findTracklist(input):
    inputList = cleanInput(input)
    trackList = []
    token = getToken()
    print("token: " + token)
    for word in inputList:
        search = searchForSongs(token, word, 0)
        for item in search['tracks']['items']:
            if word.strip().lower() in item['name'].strip().lower().split():
                trackList.append(item)
                break
    return trackList

# temporary command line output
def tracklistNames(trackList):
    for item in trackList:
        print(f"\n{item['name']} by {item['artists'][0]['name']}")

## GUI
layout = [
        [sg.Text("Please enter phrase: ")], 
        [sg.Input(key="Input", size =(15, 1))],
        [sg.Submit(), sg.Cancel()],
        [sg.Listbox(
            values = [], enable_events=True, size = (40, 20), key="Output"
        )],
        [sg.Text("Enter Playlist Name: ")], 
         [sg.Input(key="Name", size= (15, 1))],
         [sg.Button("Create Playlist")]
          ]
window = sg.Window("Playlist Creator", layout)

while True:
    event, values = window.read()
    if event == "Submit":
        trackList = findTracklist(values["Input"])
        artistSongList = []
        for item in trackList:
            artistSongList.append(f"{item['name']} by {item['artists'][0]['name']}")
        window['Output'].update(artistSongList)
    if event == "Create Playlist":
        username = "jackodom"
        playlistName = values["Name"]
        token = util.prompt_for_user_token(
            username=username,
            scope='playlist-modify-public', 
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET, 
            redirect_uri="http://localhost:8888/callback")
        sp = spotipy.Spotify(auth=token)
        sp.user_playlist_create(username, name = playlistName)
        playlists = sp.user_playlists(username)
        playlistID = ''
        for playlist in playlists['items']:  # iterate through playlists I follow
            if playlist['name'] == playlistName:  # filter for newly created playlist
                playlistID = playlist['id']
        trackIDs = []
        for item in trackList:
            trackIDs.append(item['id'])
        sp.user_playlist_add_tracks(username, playlistID, trackIDs)
        break
    if event == sg.WIN_CLOSED or event == "Cancel":
        break

window.close()
