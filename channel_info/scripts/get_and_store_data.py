from googleapiclient.discovery import build
from authenticate import authenticate  # Assuming you have a separate file for authentication
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from logger_factory import get_logger
import os
from dotenv import load_dotenv

logger = get_logger(__name__)

def get_channel_subscriptions(youtube, channel_id):
    try:
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
        logger.error(f"An error occurred while fetching channel subscriptions: {e}")
        return []

def get_video_duration(youtube, video_id):
    try:
        # Retrieve the video details
        request = youtube.videos().list(
            part='contentDetails',
            id=video_id
        )
        response = request.execute()
        
        # Extract duration from the response
        duration = response['items'][0]['contentDetails']['duration']
        
        return duration
    except Exception as e:
        logger.error(f"An error occurred while fetching video duration: {e}")
        return None

def get_channel_videos(youtube, channel_id):
    try:
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
                video_duration = get_video_duration(youtube, video_id)
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
        logger.error(f"An error occurred while fetching channel videos: {e}")
        return []

# Function to connect to the Mongo database
def conn_to_mongodb():
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        return client, collection
    except Exception as e:
        logger.error(f"An error occurred while connecting to MongoDB: {e}")
        return None

def insert_video_data(channel_id, video_id, title, published_at, duration):
    try:
        client, collection = conn_to_mongodb()
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
        logger.info('Data inserted successfully')
    except Exception as e:
        logger.error(f"An error occurred while inserting video data: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    try:
        load_dotenv()
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_DB = os.getenv('MONGO_DB')
        MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')


        # Authenticate once and pass the credentials to the functions
        credentials = authenticate()
        if not credentials:
            logger.error("Authentication failed!")
            exit(1)
        
        youtube = build('youtube', 'v3', credentials=credentials)

        channel_id = input("Enter channel ID:")
        subscriptions = get_channel_subscriptions(youtube,channel_id)
        
        print("Your Subscriptions:", subscriptions)
        
        # Get the videos uploaded by each subscribed channel
        for channel_id in subscriptions:
            logger.info(f"Videos uploaded by channel {channel_id}:")
            videos = get_channel_videos(youtube, channel_id)
            logger.info(videos)
            for video in videos:
                insert_video_data(channel_id, video['video_id'], video['title'], video['published_at'], video['duration'])
    except Exception as e:
        logger.error(f"An error occurred: {e}")