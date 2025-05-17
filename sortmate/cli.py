"""
SortMate - Main Entry Point

This script provides the main entry point for the SortMate application.
It handles authentication, sorting existing emails, and optionally setting up
real-time monitoring for new emails.

Usage:
    sortmate [--monitor] [--max-emails N] [--verbose]

Options:
    --monitor     Enable real-time email monitoring
    --max-emails  Maximum number of emails to process (default: all)
    --verbose     Enable verbose logging
"""

import argparse
import logging
import os
import signal
import sys
import time

from google.cloud import pubsub_v1
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sortmate.authenticate import get_credentials
from sortmate.sort import sort_past_emails
from sortmate.watch import start_watch
from sortmate.pubsub import callback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('sortmate')


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SortMate - Gmail Organizer')
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
        # Get configuration from environment variables
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
            logger.info("To enable monitoring, please set GOOGLE_CLOUD_PROJECT in your .env file")
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set for monitoring")
        
        subscription_name = os.environ.get('PUBSUB_SUBSCRIPTION')
        if not subscription_name:
            logger.error("PUBSUB_SUBSCRIPTION environment variable not set")
            logger.info("To enable monitoring, please set PUBSUB_SUBSCRIPTION in your .env file")
            raise ValueError("PUBSUB_SUBSCRIPTION must be set for monitoring")
        
        # Set up Gmail API watch notification
        logger.info("Setting up Gmail API watch notification")
        watch_response = start_watch(service)
        expiration = watch_response.get('expiration')
        logger.info(f"Watch notification set up. Expiration: {expiration}")
        
        # Create subscriber client
        logger.info("Creating Pub/Sub subscriber")
        try:
            subscriber = pubsub_v1.SubscriberClient()
            subscription_path = subscriber.subscription_path(project_id, subscription_name)
        except Exception as e:
            logger.error(f"Failed to create Pub/Sub subscriber: {e}")
            logger.info("Make sure you have the correct Google Cloud credentials configured")
            raise
        
        # Subscribe to the topic
        logger.info(f"Subscribing to: {subscription_path}")
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
        
        # Store subscriber for cleanup
        return subscriber, streaming_pull_future
    
    except Exception as e:
        logger.error(f"Error setting up monitoring: {e}")
        raise


def handle_shutdown(signal, frame, subscriber=None, streaming_pull_future=None):
    """Handle graceful shutdown."""
    logger.info("Shutdown signal received. Cleaning up...")
    
    if streaming_pull_future:
        try:
            streaming_pull_future.cancel()
            logger.info("Pub/Sub streaming pull future cancelled")
        except Exception as e:
            logger.error(f"Error cancelling streaming pull future: {e}")
    
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
    # Parse command line arguments
    args = parse_arguments()
    
    # Set verbose logging if requested
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('sortmate').setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    try:
        # Authenticate user
        logger.info("Authenticating with Google...")
        creds = get_credentials()
        
        # Build Gmail service
        logger.info("Building Gmail API service...")
        service = build('gmail', 'v1', credentials=creds)
        
        # Sort existing emails
        logger.info("Starting email sorting...")
        sort_past_emails(service, max_emails=args.max_emails)
        logger.info("Email sorting complete")
        
        # Set up monitoring if requested
        subscriber = None
        streaming_pull_future = None
        if args.monitor:
            logger.info("Setting up email monitoring...")
            subscriber, streaming_pull_future = setup_monitoring(service)
            
            # Register signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, 
                         lambda s, f: handle_shutdown(s, f, subscriber, streaming_pull_future))
            signal.signal(signal.SIGTERM, 
                         lambda s, f: handle_shutdown(s, f, subscriber, streaming_pull_future))
            
            # Print monitoring information
            logger.info("Monitoring active. New emails will be automatically sorted.")
            logger.info("Press Ctrl+C to exit.")
            
            # Keep the main thread alive
            try:
                # Keep the main thread alive, which keeps the process alive.
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                handle_shutdown(None, None, subscriber, streaming_pull_future)
        
    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())