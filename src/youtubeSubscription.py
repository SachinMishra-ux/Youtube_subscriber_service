# -*- coding: utf-8 -*-
import os
import google_auth_oauthlib.flow # helps with obtaining user authorization to access Google APIs securely.
import googleapiclient.discovery # It allows your Python script to interact with Google APIs
import googleapiclient.errors    # provides error-handling classes for handling API request failures.

# Define the required scopes for accessing YouTube subscriptions
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    #client_secrets_file = r"C:\Users\annum\YT_subscriptions\client_secret_336418085349-a4h9dsnocutpmhih4cj8d5kllrl0nrj2.apps.googleusercontent.com.json"  # Ensure this file is in your working directory
    client_secrets_file= '/Users/sachinmishra/Desktop/Youtube_subscriber_service/src/client_secret_336418085349-a4h9dsnocutpmhih4cj8d5kllrl0nrj2.apps.googleusercontent.com.json'

    # Authenticate user and get credentials
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(port=8080)  # Open OAuth consent screen in browser

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # Fetch user's subscriptions list
    request = youtube.subscriptions().list(
        part="snippet,contentDetails",
        mine=True,  # Fetch subscriptions of authenticated user
        maxResults=50  # Number of results per page
    )
    response = request.execute()

    # Print subscription details
    for item in response.get("items", []):
        title = item["snippet"]["title"]
        channel_id = item["snippet"]["resourceId"]["channelId"]
        print(f"Channel Name: {title}, Channel ID: {channel_id}")

if __name__ == "__main__":
    main()
