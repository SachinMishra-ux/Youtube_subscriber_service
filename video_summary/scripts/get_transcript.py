from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from logger_factory import get_logger
import os
from dotenv import load_dotenv
from get_mongo_data import conn_to_mongodb, get_unique_documents

logger = get_logger(__name__)

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        logger.info(f"Retrieved transcript for video ID {video_id}")
        return transcript
    except TranscriptsDisabled:
        logger.error(f"Transcripts are disabled for video ID {video_id}")
        return None
    except NoTranscriptFound:
        logger.error(f"No transcript found for video ID {video_id}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while retrieving transcript for video ID {video_id}: {e}")
        return None
    

if __name__ == '__main__':
    try:
        load_dotenv()
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_DB = os.getenv('MONGO_DB')
        MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')
        client, collection= conn_to_mongodb(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
        if client and collection is not None:
            logger.info("Connection to MongoDB successful!")
            unique_documents = get_unique_documents(collection)
            logger.info(f"Unique documents: {unique_documents}")

            for doc in unique_documents:
                video_id = doc['video_id']
                transcript = get_video_transcript(video_id)
                if transcript:
                    logger.info(f"Transcript for video ID {video_id}: {transcript}")
                else:
                    logger.info(f"No transcript available for video ID {video_id}")
        else:
            logger.error("Failed to connect to MongoDB")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)