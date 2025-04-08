import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

ANCHOR_API_KEY = os.getenv("ANCHOR_API_KEY")

def create_anchor_browser_session():
    try:
        response = requests.post(
            "https://api.anchorbrowser.io/v1/sessions",
            headers={
                "anchor-api-key": ANCHOR_API_KEY,
                "Content-Type": "application/json",
            },
            json={
              "browser": {
                "headless": {"active": False} # Use headless false to view the browser when combining with browser-use
              }
            })

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        response_json = response.json()  # Parse JSON response

        print("Anchor Browser session created successfully!")  # Add print statement
        print(f"Response: {response_json}")  # Print the entire response for debugging

        # Access the data object from the response
        session_data = response_json["data"]
        print(f"Session data: {session_data}")  # Print session data

        return session_data['id']

    except requests.exceptions.RequestException as e:
        print(f"Error creating Anchor Browser session: {e}")  # Print error message
        return None
    except KeyError as e:
        print(f"Error accessing session data: {e}")  # Print KeyError
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # Catch any other exceptions
        return None