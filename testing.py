from authenticate import authenticate  # for user authentication
from sort import sort_past_emails  # for sorting logic
from pubsub import callback  # for processing pubsub notifications
from watch import start_watch # for asking gmail to provide notifications for new emails
from googleapiclient.discovery import build  # to create gmail api service object
from googleapiclient.errors import HttpError # to handle errors during api calls
import time # to help with listening


if __name__ == "__main__":
    # authenticate user
    creds = authenticate()

    # build gmail service
    service = build('gmail', 'v1', credentials=creds)

    # sort existing emails
    sort_past_emails(service)

    """
    # begin watching out for emails
    start_watch(service)

    # create subscriber client 
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = 'projects/emailorganizer-445912/subscriptions/email_notifications-sub'
    subscriber.subscribe(subscription_path, callback=callback())

    # have script run indefinitely
    print("Listening for messages...")
    while True:
        time.sleep(60)
    """