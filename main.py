from handlers.PlaylistHandler import Client

def main():
    user_id = input ("Please enter user id/username (NOTE: this is different from your display name, this can be found in account ovierview)\n")
    cli = Client (user_id)
    playlist_url = cli.generateTop50()
    print(f"Playlist url: {playlist_url}\n")
    
main()