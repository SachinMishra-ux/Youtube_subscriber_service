from googleapiclient.discovery import build
from authenticate import authenticate  # Assuming you have a separate file for authentication
from pymongo import MongoClient, errors
from datetime import datetime, timedelta, timezone

MONGO_URI= "mongodb+srv://locdataquery:2rrq2k5AFtHESMju@cluster0.wsb6s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB= 'youtubedata'
MONGO_COLLECTION= 'youtube_collection'

def get_channel_subscriptions(channel_id):
    try:
        # Authenticate with the YouTube Data API
        youtube = build('youtube', 'v3', credentials=authenticate())

        # Retrieve the subscribers of the specified channel
        subscribers = []
        next_page_token = None
        while True:
            request = youtube.subscriptions().list(
                part='snippet',
                channelId=channel_id,
                maxResults=2,  # Max results per page
                pageToken=next_page_token
            )
            response = request.execute()

            # Extract subscriber data from the response
            for item in response.get('items', []):
                subscriber_id = item['snippet']['resourceId']['channelId']
                subscribers.append(subscriber_id)

            # Check if there are more pages of subscribers
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break  # Exit loop if there are no more pages

        return subscribers
    except Exception as e:
        print(f"An error occurred while fetching channel subscriptions: {e}")
        return []

def get_video_duration(video_id):
    try:
        youtube = build('youtube', 'v3', credentials=authenticate())
        
        request = youtube.videos().list(
            part='contentDetails',
            id=video_id
        )
        response = request.execute()
        
        # Extract duration from the response
        duration = response['items'][0]['contentDetails']['duration']
        
        return duration
    except Exception as e:
        print(f"An error occurred while fetching video duration: {e}")
        return None

def get_channel_videos(channel_id):
    try:
        # Authenticate with the YouTube Data API
        youtube = build('youtube', 'v3', credentials=authenticate())

        # Calculate the date range for today
        today = datetime.now(timezone.utc).date()
        tomorrow = today + timedelta(days=1)
        today_iso = today.isoformat() + 'T00:00:00Z'
        tomorrow_iso = tomorrow.isoformat() + 'T00:00:00Z'

        # Retrieve videos uploaded by the specified channel within the date range of today
        videos = []
        next_page_token = None
        while True:
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                maxResults=50,  # Max results per page
                order='date',  # Order by date
                publishedAfter=today_iso,
                publishedBefore=tomorrow_iso,
                pageToken=next_page_token
            )
            response = request.execute()

            # Extract video data from the response
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                video_title = item['snippet']['title']
                video_published_at = item['snippet']['publishedAt']
                
                # Fetch video duration
                video_duration = get_video_duration(video_id)
                if video_duration:
                    videos.append({
                        'video_id': video_id,
                        'title': video_title,
                        'published_at': video_published_at,
                        'duration': video_duration
                    })

            # Check if there are more pages of videos
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break  # Exit loop if there are no more pages

        return videos
    except Exception as e:
        print(f"An error occurred while fetching channel videos: {e}")
        return []

# Function to connect to the Mongo database
def conn_to_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        return client, collection
    except errors.ConnectionError as e:
        print(f"An error occurred while connecting to MongoDB: {e}")
        return None, None

def insert_video_data(channel_id, video_id, title, published_at, duration):
    client, collection = conn_to_mongodb()
    if not client or not collection:
        return

    try:
        # Convert published_at to the correct datetime format
        datetime_obj = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
        formatted_published_at = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

        # Document to be inserted into MongoDB
        document = {
            'channel_id': channel_id,
            'video_id': video_id,
            'title': title,
            'published_at': formatted_published_at,
            'duration': duration
        }

        # Insert the document into the collection
        collection.insert_one(document)
        print('Data inserted successfully')
    except Exception as e:
        print(f"An error occurred while inserting video data: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    try:
        channel_id = input("Enter channel ID:")
        subscriptions = get_channel_subscriptions(channel_id)
        print("Your Subscriptions:", subscriptions)
        
        # Get the videos uploaded by each subscribed channel
        for channel_id in subscriptions:
            print(f"Videos uploaded by channel {channel_id}:")
            videos = get_channel_videos(channel_id)
            print(videos)
            for video in videos:
                insert_video_data(channel_id, video['video_id'], video['title'], video['published_at'], video['duration'])
    except Exception as e:
        print(f"An error occurred: {e}")