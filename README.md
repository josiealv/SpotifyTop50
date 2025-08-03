# Spotify Top 50 Playlist Generator

Automatically generates and updates a "My Top 50" Spotify playlist with your current top tracks.

## Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd SpotifyTop50
```

### 2. Install Dependencies
```bash
pip3 install spotipy python-dotenv
```

### 3. Spotify API Setup
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy your Client ID and Client Secret
4. Set redirect URI to `http://localhost:8080`

### 4. Environment Variables
Create a `.env` file in the project root:
```
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://localhost:8080
```

### 5. Update Script Path
Edit `top50.sh` and replace the path with your actual project location:
```bash
cd /path/to/your/SpotifyTop50
```

### 6. Make Script Executable
```bash
chmod +x top50.sh
```

## Usage

### Manual Run
```bash
./top50.sh
```

### Automated Weekly Updates

#### Option 1: Cron (Recommended)
Run every Sunday at 10 PM:
```bash
echo "0 22 * * 0 /path/to/your/SpotifyTop50/top50.sh" | crontab -
```

Verify cron job:
```bash
crontab -l
```

#### Option 2: macOS launchd
1. Update the path in `com.spotify.top50.plist`
2. Copy to LaunchAgents:
```bash
cp com.spotify.top50.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.spotify.top50.plist
```

## How It Works

1. Fetches your top 50 tracks from Spotify
2. Creates or updates "My Top 50" playlist
3. Maintains exactly 50 tracks, updating only what changed
4. Runs weekly to keep your playlist current

## Troubleshooting

- **Authentication issues**: Delete `.cache-<username>` file and re-run
- **Permission errors**: Ensure script has execute permissions
- **Path issues**: Use absolute paths in cron jobs
- **Clear cache**: The script automatically clears Python cache before running