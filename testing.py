from authenticate import authenticate  # For user authentication
from fetch_emails import get_all_emails  # For fetching emails
from sort import sort_past_emails  # For sorting logic
from pubsub import callback  # For processing Pub/Sub notifications
from googleapiclient.discovery import build  # To create Gmail API service object
import time 


if __name__ == "__main__":
    # authenticate and build Gmail service
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    # sort existing emails
    sort_past_emails(service)

    # begin watching out for emails
    start_watch(service)

    # create subscriber client 
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = 'projects/emailorganizer-445912/subscriptions/email_notifications-sub'
    subscriber.subscribe(subscription_path, callback=callback)

    # have script run indefinitely
    print("Listening for messages...")
    while True:
        time.sleep(60)