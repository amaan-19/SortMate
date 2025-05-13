"""
Gmail Organizer - Main Entry Point

This script provides the main entry point for the Gmail Organizer application.
It handles authentication, sorting existing emails, and optionally setting up
real-time monitoring for new emails.

Usage:
    python testing.py [--monitor] [--max-emails N] [--verbose]

Options:
    --monitor     Enable real-time email monitoring
    --max-emails  Maximum number of emails to process (default: all)
    --verbose     Enable verbose logging
"""

import argparse
import logging
import signal
import sys
import time

from google.cloud import pubsub_v1
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from authenticate import authenticate
from sort import sort_past_emails
from watch import start_watch
from pubsub import callback


# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('gmail_organizer')


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Gmail Organizer')
    parser.add_argument('--monitor', action='store_true', 
                        help='Enable real-time email monitoring')
    parser.add_argument('--max-emails', type=int, default=None, 
                        help='Maximum number of emails to process')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()


def setup_monitoring(service):
    """Set up real-time email monitoring with Pub/Sub."""
    try:
        logger.info("Setting up Gmail API watch notification")
        watch_response = start_watch(service)
        logger.info(f"Watch notification set up. Expiration: {watch_response.get('expiration')}")
        
        # create subscriber client
        logger.info("Creating Pub/Sub subscriber")
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = 'projects/emailorganizer-445912/subscriptions/email_notifications-sub'
        
        # subscribe to the topic
        logger.info(f"Subscribing to: {subscription_path}")
        subscriber.subscribe(subscription_path, callback=callback)
        
        return subscriber
    except Exception as e:
        logger.error(f"Error setting up monitoring: {e}")
        raise


def handle_shutdown(signal, frame, subscriber=None):
    """Handle graceful shutdown."""
    logger.info("Shutdown signal received. Cleaning up...")
    
    if subscriber:
        try:
            subscriber.close()
            logger.info("Pub/Sub subscriber closed")
        except Exception as e:
            logger.error(f"Error closing subscriber: {e}")
    
    logger.info("Shutdown complete")
    sys.exit(0)


def main():
    """Main entry point."""
    # parse command line arguments
    args = parse_arguments()
    
    # set verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    try:
        # authenticate user
        logger.info("Authenticating with Google...")
        creds = authenticate()
        
        # build Gmail service
        logger.info("Building Gmail API service...")
        service = build('gmail', 'v1', credentials=creds)
        
        # sort existing emails
        logger.info("Starting email sorting...")
        sort_past_emails(service, max_emails=args.max_emails)
        logger.info("Email sorting complete")
        
        # set up monitoring if requested
        subscriber = None
        if args.monitor:
            logger.info("Setting up email monitoring...")
            subscriber = setup_monitoring(service)
            
            # register signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, lambda s, f: handle_shutdown(s, f, subscriber))
            signal.signal(signal.SIGTERM, lambda s, f: handle_shutdown(s, f, subscriber))
            
            # run indefinitely
            logger.info("Listening for new emails. Press Ctrl+C to exit.")
            while True:
                time.sleep(60)
        
    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())