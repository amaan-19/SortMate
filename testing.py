from authenticate import authenticate  # for user authentication
from sort import sort_past_emails  # for sorting logic
from googleapiclient.discovery import build  # to create gmail api service object


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