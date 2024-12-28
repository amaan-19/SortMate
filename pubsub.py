from google.cloud import pubsub_v1

def callback(message):
    """Process new email notifications."""
    import json
    try:
        # Parse the message data
        data = json.loads(message.data)
        print(f"Parsed message data: {data}")

        # Extract Gmail-specific details (if available)
        history_id = data.get('historyId')
        if history_id:
            print(f"Processing history ID: {history_id}")
            # Add your Gmail API call here to fetch email details

    except Exception as e:
        print(f"Error processing message: {e}")

    # acknowledge message was received
    message.ack()
    # Fetch the email using the Gmail API and apply sorting logic