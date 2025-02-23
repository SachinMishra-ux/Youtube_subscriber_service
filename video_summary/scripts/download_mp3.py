from logger_factory import get_logger
import os
from dotenv import load_dotenv
from get_mongo_data import conn_to_mongodb, get_unique_documents

import yt_dlp
import boto3
import os
import time

logger = get_logger(__name__)



def download_audio(youtube_url, output_dir='audio_files'):
    """Download audio from YouTube video URL."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Download audio in MP3 format using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        file_name = f"{info_dict['id']}.mp3"
        file_path = os.path.join(output_dir, file_name)
        return file_path   
    
def upload_to_s3(file_path, s3_bucket, s3_key):
    """Upload the audio file to AWS S3."""
    s3_client.upload_file(file_path, s3_bucket, s3_key)
    print(f"File uploaded to S3: s3://{s3_bucket}/{s3_key}")
    
if __name__ == "__main__":
    try:

        load_dotenv()
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_DB = os.getenv('MONGO_DB')
        MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')
        # Set your AWS S3 bucket details
        BUCKET_NAME = os.getenv('BUCKET_NAME')
        OUTPUT_BUCKET_NAME = os.getenv('OUTPUT_BUCKET_NAME')
        AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')  # Default to 'ap-south-1' if not set

        # AWS Setup
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        transcribe_client = boto3.client('transcribe', region_name=AWS_REGION)

        client, collection= conn_to_mongodb(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
        
        logger.info("Connection to MongoDB successful!")
        unique_documents = get_unique_documents(collection)
        logger.info(f"Unique documents: {unique_documents}")

        youtube_url= "https://www.youtube.com/watch?v="
        for doc in unique_documents:
            video_id = doc['video_id']

            # Download audio from YouTube video URL
            #youtube_url = "https://www.youtube.com/watch?v=Y5GnrFluotA"
            audio_file_path = download_audio(youtube_url+video_id)
            print(f"Audio file downloaded: {audio_file_path}")

            # Step 2: Upload the audio to S3
            s3_key = os.path.basename(audio_file_path)
            upload_to_s3(audio_file_path, BUCKET_NAME, s3_key)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
# Output: Audio file downloaded: audio_files/9bZkp7q19f0.mp3