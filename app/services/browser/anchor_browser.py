import requests
from dotenv import load_dotenv
from httpx import AsyncClient

import os

# Load environment variables
load_dotenv()

ANCHOR_API_KEY = os.getenv("ANCHOR_API_KEY")



async def create_anchor_browser_session():
    try:
        async with AsyncClient() as client:
            response = await client.post(
                "https://api.anchorbrowser.io/v1/sessions",
                headers={
                    "anchor-api-key": ANCHOR_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "browser": {
                        "headless": {"active": False}
                    }
                }
            )

            response.raise_for_status()
            response_json = response.json()

            print("Anchor Browser session created successfully!")
            print(f"Response: {response_json}")

            session_data = response_json["data"]
            print(f"Session data: {session_data}")

            return (
                session_data['id'],
                session_data['cdp_url'],
                session_data.get('live_view_url')
            )
    except Exception as e:
        print(f"Error creating Anchor Browser session: {e}")
        return None, None, None