import json
from models.track import Track
from models.playlist import Playlist
from models.removeTrack import RemoveTrack
import utils.constants as constants
from dotenv import load_dotenv
load_dotenv()
import os
import spotipy
import spotipy.util as util
from spotipy.exceptions import SpotifyException

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

class Client:
    def __init__(self, user_id):
        self.user_id = user_id
        self.auth_token = self.getToken()

    def getToken(self):
        SCOPES = [
            "playlist-modify-public",
            "playlist-modify-private",
            "playlist-read-private",
            "user-top-read"
        ]
        token = util.prompt_for_user_token(self.user_id, SCOPES, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)

        try:
            if token:
                sp = spotipy.Spotify(auth=token)        
                return sp 
            else:
                raise PermissionError("There was a problem generating a token")
        except PermissionError as error:
            print ("PermissionError: " + error)

    def generateTop50(self):
      playlist = self.getTop50Playlist()
      self.generateTrackList(playlist)
      return playlist.url

    def getTop50Playlist(self):
        DESCRIPTION = "My top 50 tracks - Playlist generated programatically"
        MY_TOP_50 = "My Top 50"
        users_playlists = self.auth_token.current_user_playlists()

        for playlist in users_playlists[constants.ITEMS]:
                if (playlist[constants.NAME] == MY_TOP_50):
                    return Playlist(playlist[constants.NAME], playlist[constants.ID], playlist["external_urls"]["spotify"])

        newPlaylist = self.auth_token.user_playlist_create(self.user_id, name=MY_TOP_50, description=DESCRIPTION)
        return Playlist(MY_TOP_50, newPlaylist[constants.ID], newPlaylist["external_urls"]["spotify"]) # use json response to create Playlist object
    
    def generateTrackList(self, playlist):
        top50 = self.getNewTracks(0, 50)

        # Used to check if we are updating playlist tracks or adding tracks to newly created playlist
        top50Playlist = self.auth_token.playlist(playlist_id=playlist.id)
        if not constants.ITEMS in top50Playlist[constants.TRACKS] or len(top50Playlist[constants.TRACKS][constants.ITEMS]) == 0:
            self.createNewTrackList(top50, playlist.id)
        else:
            self.updateTrackList(top50, playlist)
    
    def getNewTracks(self, offset, limit):
        user_top_tracks = self.auth_token.current_user_top_tracks(limit, offset, "long_term") ## only gets 50
        return [Track(track[constants.ID], track[constants.URI], 
                    track[constants.NAME], track[constants.ARTISTS][0][constants.NAME])
                 for track in user_top_tracks[constants.ITEMS]]
    
    def getOldTracks (self, playlist):
        user_current_tracks = self.auth_token.user_playlist_tracks(user=self.user_id, playlist_id=playlist.id)
        return [Track(track[constants.TRACK][constants.ID], track[constants.TRACK][constants.URI], 
                      track[constants.TRACK][constants.NAME], track[constants.TRACK][constants.ARTISTS][0][constants.NAME]) 
                      for track in user_current_tracks[constants.ITEMS]]

    def updateTrackList(self, newTracks, top50Playlist):
        oldTracks = self.getOldTracks(top50Playlist)
        currSize = len(oldTracks)

        # This would usually be 50 but users might remove tracks after creation 
        # so this only updates/removes based on number of tracks (currSize)
        # and adds whatever is left over from newTracks separately
        #
        # Ex: if there are currently 10 tracks in playlist, we check if those 10 tracks' 
        # rankings changed/have been replaced and update those 10. 
        # The remaining 40 get added without question
        for i in range (currSize):
            if (oldTracks[i].id != newTracks[i].id):
                oldTrackList = []
                newTrackList = []
                print("tracks don't match!\n")
                print(f"{i+1}. Current track: {oldTracks[i].name} \n")
                print(f"{i+1}. New track: {newTracks[i].name} \n")
                oldTrackList.append({
                    "uri": oldTracks[i].uri,
                    "positions": [i]
                 })
                newTrackList.append(newTracks[i].id)
                try:
                    self.auth_token.playlist_remove_specific_occurrences_of_items(top50Playlist.id, json.loads(json.dumps(oldTrackList)))
                    self.auth_token.playlist_add_items(top50Playlist.id, newTrackList, i)
                except(SpotifyException):
                    self.auth_token.playlist_remove_all_occurrences_of_items(top50Playlist.id, oldTracks[i])
                    self.auth_token.playlist_add_items(top50Playlist.id, newTrackList)

        if(currSize<50):
            remainingTrackList = []
            for j in range (currSize, 50):
                print(f"{j+1}. New track: {newTracks[j].name}")
                remainingTrackList.append(newTracks[j].id)
            self.auth_token.playlist_add_items(top50Playlist.id, remainingTrackList, currSize)
    
    def createNewTrackList(self, top50Tracks, top50PlaylistID):
       trackList = []
       for track in top50Tracks:
            trackList.append(track.id)
       self.auth_token.playlist_add_items(top50PlaylistID, trackList)