# Copyright 2022 Maciej Kaszkowiak (maciej@kaszkowiak.org)
# Apache License 2.0
import requests
import json
import unicodedata
import escpos.printer
from time import strftime, localtime, sleep
from datetime import datetime


def ascii(x):
    """Converts the text to be suitable for ASCII print: ć -> c, ą -> a, etc."""
    return unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode('ascii')

def fetchScrobbles(username, api_key):
    """Returns 5 most recent last.fm user scrobbles.
    Uses the user.getRecentTracks API endpoint
    Response is returned as a dictionary converted from JSON""" 
    payload = {
        'api_key': api_key, 
        'method': 'user.getRecentTracks',
        'user': username,
        'format': 'json',
        'limit': 5
    }
    r = requests.get('https://ws.audioscrobbler.com/2.0/', params=payload)
    return r.json()

def getScrobbleTime(track):
    """Returns None if now playing, otherwise returns a datetime object"""
    return None if 'date' not in track else datetime.fromtimestamp(int(track['date']['uts']))

def getScrobbleId(track):
    """Returns unique scrobble ID. We will treat the timestamp as an identifier"""
    return track['date']['uts'] 

def getScrobbleOverview(track):
    """Returns the text to be printed for a scrobble. 
    Returns None if the scrobble is marked as Now Playing."""
    time_ts = getScrobbleTime(track)
    if not time_ts:
        return None

    time_str = f"{time_ts:%Y-%m-%d %H:%M:%S}"
    artist = ascii(track['artist']['#text'])
    album = ascii(track['album']['#text'])
    title = ascii(track['name'])

    template = f"\n{time_str}"
    template += f"\n@{username}"
    template += f"\n{artist}"
    template += f"\n{title}"
    template += f"\n---------------------\n"

    return template

def log(message):
    """Wrapper for the print function to make things more neat"""
    current_time = strftime("%H:%M:%S", localtime())
    print(f"[{current_time}] {message}")


class ScrobblePrinter:
    def __init__(self, serial_port, api_key):
        self.__api_key = api_key
        self.printer_connection = escpos.printer.Serial(serial_port)
        self.user_recent_scrobble = {}

    def __del__(self):
        self.printer_connection.cut()

    def checkUserScrobbles(self, username):
        # log(f"Downloading scrobbles for {username} from the API")
        response = fetchScrobbles(username, api_key=self.__api_key)

        if username not in self.user_recent_scrobble:
            self.user_recent_scrobble[username] = None

        if not ('recenttracks' in response) or not ('track' in response['recenttracks']):
            log(f"[!] Error downloading scrobbles for {username}, doubling wait and omitting turn")
            log(response)
            return False

        for track in response['recenttracks']['track']:
            now_playing = not getScrobbleTime(track)
            if now_playing:
                # log(f"Omitting {username}'s currently playing track") 
                continue

            scrobble_id = getScrobbleId(track)
            if scrobble_id == self.user_recent_scrobble[username]:
                # log(f"{username}'s most recent scrobble didn't change with an ID of {scrobble_id}")
                pass 
            else:
                # New scrobble!
                scrobble = getScrobbleOverview(track)
                log(scrobble)
                self.printer_connection.text(scrobble)

            # We've checked the most recent scrobble, don't check further
            self.user_recent_scrobble[username] = scrobble_id
            break

        return True

if __name__ == "__main__":
    # =====================
    # | Modify this part! |
    # =====================
    USERNAMES           = ['username1', 'username2', 'and so on']
    SERIAL_PORT         = '<serial port, for ex. COM5>'
    API_KEY             = "<your last.fm API key>"
    REQUEST_DELAY_SEC   = 3

    username_index = 0
    scrobble_printer = ScrobblePrinter(serial_port=SERIAL_PORT, api_key=API_KEY)
    while True:
        username = USERNAMES[username_index]
        username_index = (username_index + 1) % len(USERNAMES)

        success = scrobble_printer.checkUserScrobbles(username)
        if success:
            sleep(REQUEST_DELAY_SEC)
        else:
            sleep(REQUEST_DELAY_SEC * 2)    
