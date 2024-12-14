import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
import datetime
import os
from dotenv import load_dotenv
import gspread

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = os.getenv("SCOPE")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope=SCOPE))

top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range='short_term')

def get_track_ids(time_frame):
  track_ids = []
  for song in time_frame['items']:
    track_ids.append(song['id'])
  return track_ids

track_ids = get_track_ids(top_tracks)

def get_track_features(id):
  meta = sp.track(id)
  name = meta['name']
  album = meta['album']['name']
  artist = meta['album']['artists'][0]['name']
  spotify_url = meta['external_urls']['spotify']
  album_cover = meta['album']['images'][0]['url']
  track_info = [name, album, artist, spotify_url, album_cover]
  return track_info

tracks = []
for i in range(len(track_ids)):
  time.sleep(.5)
  track = get_track_features(track_ids[i])
  tracks.append(track)

df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover'])

gc = gspread.service_account(filename='my-wrapped-444606-b18ea2aa0859.json')

sh = gc.open('My Wrapped')

worksheet = sh.worksheet('short_term')

def insert_to_gsheet(track_ids, time_period):
  tracks = []
  for i in range(len(track_ids)):
    time.sleep(.5)
    track = get_track_features(track_ids[i])
    tracks.append(track)
  df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'spotify_url', 'album_cover'])
  gc = gspread.service_account(filename='my-wrapped-444606-b18ea2aa0859.json')
  sh = gc.open('My Wrapped')
  worksheet = sh.worksheet(f'{time_period}')
  worksheet.update([df.columns.values.tolist()] + df.values.tolist())
  print(f'{time_period} data inserted successfully!')

time_ranges = ['short_term', 'medium_term', 'long_term']
for time_period in time_ranges:
  top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range=time_period)
  track_ids = get_track_ids(top_tracks)
  insert_to_gsheet(track_ids, time_period)
