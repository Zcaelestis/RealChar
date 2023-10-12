import httpx

class GreenApiClient:
    BASE_URL = "https://api.greenapi.com/instance7103865679/"  # 更新实例ID
    TOKEN = "0acca0d7f38e4a2d82a331cbba76e565132de8d6aff3413faf"  # API

    def send_message(self, phone_number, text):
        url = f"{self.BASE_URL}sendMessage?token={self.TOKEN}"
        data = {
            "phone": phone_number,
            "body": text
        }
        response = httpx.post(url, json=data)
        return response.json()
