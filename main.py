import os
from dotenv import load_dotenv
import googleapiclient.discovery
from youtube_transcript_api import YouTubeTranscriptApi
import json

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("Please set YOUTUBE_API_KEY in your .env file")

# Initialize YouTube API client
youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=API_KEY)

# Get the channel ID for @DWNews
search_request = youtube.search().list(
    part='snippet',
    q='@DWNews',
    type='channel',
    maxResults=1
)
search_response = search_request.execute()
channel_id = search_response['items'][0]['snippet']['channelId']

# Get the uploads playlist ID
channel_request = youtube.channels().list(
    part='contentDetails',
    id=channel_id
)
channel_response = channel_request.execute()
uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Get video IDs (first 10 for demo)
playlist_request = youtube.playlistItems().list(
    part='contentDetails',
    playlistId=uploads_playlist_id,
    maxResults=10
)
playlist_response = playlist_request.execute()
video_ids = [item['contentDetails']['videoId'] for item in playlist_response['items']]

# Fetch transcripts
transcripts = {}
for video_id in video_ids:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'de'])
        transcripts[video_id] = transcript
        print(f"Fetched transcript for {video_id}")
    except Exception as e:
        print(f"Failed to fetch transcript for {video_id}: {e}")

# Save to file
with open('dw_transcripts.json', 'w') as f:
    json.dump(transcripts, f, indent=2)

print("Transcripts saved to dw_transcripts.json")