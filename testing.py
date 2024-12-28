from googleapiclient.discovery import build
from fetch_emails import *
from sort_emails import *
from watch_request import *
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