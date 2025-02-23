from pymongo import MongoClient

from logger_factory import get_logger
import os
from dotenv import load_dotenv

logger = get_logger(__name__)

def conn_to_mongodb(MONGO_URI,MONGO_DB,MONGO_COLLECTION):
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        return client, collection
    except Exception as e:
        logger.error(f"An error occurred while connecting to MongoDB: {e}")
        return None

def get_unique_documents(collection):
    try:
        # Retrieve unique documents from the collection where duration is greater than 1 minute
        pipeline = [
            {
                "$match": {
                    "duration": {"$regex": "^PT([1-9][0-9]M|[2-9]M|[1-9][0-9]+M)"}
                }
            },
            {
                "$group": {
                    "_id": "$video_id",
                    "doc": {"$first": "$$ROOT"}
                }
            }
        ]
        unique_documents = list(collection.aggregate(pipeline))
        logger.info(f"Retrieved {len(unique_documents)} unique documents from the collection")
        return [doc['doc'] for doc in unique_documents]
    except Exception as e:
        logger.error(f"An error occurred while retrieving unique documents: {e}")
        return []  

    
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
        else:
            logger.error("Failed to connect to MongoDB")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        exit(1)
