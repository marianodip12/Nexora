from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
import json
import os


class WhatsAppMessageRequest(BaseModel):
    """Input schema for WhatsApp Messenger Tool."""
    recipient_phone_number: str = Field(
        ...,
        description="The recipient's phone number in international format (including country code, e.g., '+1234567890')"
    )
    message_text: str = Field(
        ...,
        description="The text message to send. Supports Unicode characters including Spanish text."
    )


class WhatsAppMessengerTool(BaseTool):
    """Tool for sending messages via WhatsApp Business Cloud API."""

    name: str = "whatsapp_messenger"
    description: str = (
        "Sends text messages through WhatsApp Business Cloud API. "
        "Requires WHATSAPP_ACCESS_TKN and WHATSAPP_PHONE_ID environment variables. "
        "Accepts recipient phone number in international format and message text. "
        "Returns success status with message details or error information."
    )
    args_schema: Type[BaseModel] = WhatsAppMessageRequest

    def _run(self, recipient_phone_number: str, message_text: str) -> str:
        """
        Send a WhatsApp message using the Cloud API.
        
        Args:
            recipient_phone_number: Phone number in international format
            message_text: Text message to send
            
        Returns:
            JSON string with success/failure status and details
        """
        try:
            # Get environment variables
            whatsapp_token = os.getenv('WHATSAPP_ACCESS_TKN')
            whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_ID')
            
            if not whatsapp_token:
                return json.dumps({
                    "success": False,
                    "error": "WHATSAPP_ACCESS_TKN environment variable not set",
                    "error_code": "MISSING_TOKEN"
                }, ensure_ascii=False)
            
            if not whatsapp_phone_id:
                return json.dumps({
                    "success": False,
                    "error": "WHATSAPP_PHONE_ID environment variable not set",
                    "error_code": "MISSING_PHONE_ID"
                }, ensure_ascii=False)
            
            # Validate recipient phone number
            if not recipient_phone_number.strip():
                return json.dumps({
                    "success": False,
                    "error": "Recipient phone number cannot be empty",
                    "error_code": "INVALID_PHONE"
                }, ensure_ascii=False)
            
            # Clean phone number (remove spaces, dashes, etc.)
            cleaned_phone = ''.join(filter(str.isdigit, recipient_phone_number))
            
            # Validate message text
            if not message_text.strip():
                return json.dumps({
                    "success": False,
                    "error": "Message text cannot be empty",
                    "error_code": "EMPTY_MESSAGE"
                }, ensure_ascii=False)
            
            # WhatsApp Cloud API endpoint
            url = f"https://graph.facebook.com/v18.0/{whatsapp_phone_id}/messages"
            
            # Request headers
            headers = {
                "Authorization": f"Bearer {whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            # Request payload according to WhatsApp Cloud API specifications
            payload = {
                "messaging_product": "whatsapp",
                "to": cleaned_phone,
                "type": "text",
                "text": {
                    "body": message_text
                }
            }
            
            # Make the API request
            response = requests.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                return json.dumps({
                    "success": True,
                    "message": "WhatsApp message sent successfully",
                    "recipient": cleaned_phone,
                    "message_text": message_text,
                    "message_id": response_data.get("messages", [{}])[0].get("id"),
                    "whatsapp_id": response_data.get("messages", [{}])[0].get("wa_id"),
                    "status_code": response.status_code
                }, ensure_ascii=False)
            else:
                # Handle error response
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    error_code = error_data.get("error", {}).get("code", "UNKNOWN")
                except:
                    error_message = f"HTTP {response.status_code}: {response.text}"
                    error_code = f"HTTP_{response.status_code}"
                
                return json.dumps({
                    "success": False,
                    "error": f"WhatsApp API error: {error_message}",
                    "error_code": error_code,
                    "status_code": response.status_code,
                    "recipient": cleaned_phone
                }, ensure_ascii=False)
                
        except requests.exceptions.Timeout:
            return json.dumps({
                "success": False,
                "error": "Request timeout - WhatsApp API did not respond within 30 seconds",
                "error_code": "TIMEOUT"
            }, ensure_ascii=False)
            
        except requests.exceptions.ConnectionError:
            return json.dumps({
                "success": False,
                "error": "Connection error - Unable to reach WhatsApp API",
                "error_code": "CONNECTION_ERROR"
            }, ensure_ascii=False)
            
        except requests.exceptions.RequestException as e:
            return json.dumps({
                "success": False,
                "error": f"Request error: {str(e)}",
                "error_code": "REQUEST_ERROR"
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNEXPECTED_ERROR"
            }, ensure_ascii=False)