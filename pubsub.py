from google.cloud import pubsub_v1
import json


def callback(message):
    try:
        # parse message data
        data = json.loads(message.data)
        print(f"Parsed message data: {data}")

        # extract gail-specific details (if available)
        history_id = data.get('historyId')
        if history_id:
            print(f"Processing history ID: {history_id}")
            # add your gmail API call here to fetch email details

    except Exception as e:
        print(f"Error processing message: {e}")

    # acknowledge message was received
    message.ack()
    # fetch the email using the gmail API and apply sorting logic