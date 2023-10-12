import os
import httpx
from typing import Optional

class RealCharIntegration:
    BASE_URL = "http://localhost:8000"

    @staticmethod
    def send_request_to_realchar(character_id: str, user_input: str, config_path: str) -> Optional[str]:
        url = f"{RealCharIntegration.BASE_URL}/interact/{character_id}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "query": user_input,
            "config_path": config_path
        }

        try:
            response = httpx.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json().get("response", None)
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

def get_response_from_elon_musk(query: str) -> Optional[str]:
    character_id = "elon_musk"
    config_path = "C:\\Users\\zhang\\Desktop\\RealChar-main\\RealChar-main\\realtime_ai_character\\character_catalog\\elon_musk\\config.yaml"
    return RealCharIntegration.send_request_to_realchar(character_id, query, config_path)

if __name__ == "__main__":
    response = get_response_from_elon_musk("Tell me about SpaceX.")
    if response:
        print(response)
    else:
        print("No response received.")
