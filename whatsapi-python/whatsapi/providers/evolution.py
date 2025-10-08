"""Evolution API provider implementation"""

import aiohttp
import logging
from typing import Dict, Any, Optional
from .base import WhatsAppProvider

logger = logging.getLogger(__name__)


class EvolutionAPIError(Exception):
    """Base exception for Evolution API errors"""
    pass


class EvolutionAPIConnectionError(EvolutionAPIError):
    """Raised when connection to Evolution API fails"""
    pass


class EvolutionAPITimeoutError(EvolutionAPIError):
    """Raised when request times out"""
    pass


class EvolutionAPIProvider(WhatsAppProvider):
    """
    Evolution API provider implementation.
    
    This provider implements the WhatsAppProvider interface for Evolution API,
    handling all HTTP communication and message sending operations.
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        instance_name: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Evolution API provider.
        
        Args:
            base_url: Evolution API base URL (e.g., "http://localhost:8080")
            api_key: API key for authentication
            instance_name: WhatsApp instance name
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.timeout = timeout
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        
        logger.info(
            f"Evolution API Provider initialized: {base_url} "
            f"(instance: {instance_name})"
        )
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create aiohttp session.
        
        Returns:
            Active aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"apikey": self.api_key},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            logger.debug("Created new aiohttp session")
        return self._session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Evolution API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON payload for request body
            retry_count: Current retry attempt number
            
        Returns:
            JSON response from API
            
        Raises:
            aiohttp.ClientError: If request fails after all retries
        """
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, json=json_data) as response:
                response.raise_for_status()
                result = await response.json()
                logger.debug(f"Request successful: {method} {endpoint}")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {method} {endpoint} - {e}")
            
            # Retry logic
            if retry_count < self.max_retries:
                logger.info(f"Retrying... (attempt {retry_count + 1}/{self.max_retries})")
                return await self._make_request(method, endpoint, json_data, retry_count + 1)
            
            # Max retries reached
            raise
    
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Send text message via Evolution API.
        
        Args:
            to: Recipient phone number (e.g., "+972501234567")
            text: Message text content
            
        Returns:
            Dict containing the API response with message status
            
        Raises:
            aiohttp.ClientError: If message sending fails
        """
        # Remove + from phone number if present
        number = to.lstrip('+')
        
        endpoint = f"/message/sendText/{self.instance_name}"
        payload = {
            "number": number,
            "text": text
        }
        
        logger.info(f"Sending text message to {to}")
        return await self._make_request("POST", endpoint, payload)
    
    async def send_media_message(
        self,
        to: str,
        media_url: str,
        media_type: str,
        caption: Optional[str] = None,
        mime_type: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send media message via Evolution API.
        
        Args:
            to: Recipient phone number
            media_url: URL of the media file to send
            media_type: Type of media ("image", "video", "audio", "document")
            caption: Optional caption for the media
            mime_type: MIME type (e.g., "image/png", "video/mp4")
            file_name: Optional filename for documents
            
        Returns:
            Dict containing the API response with message status
            
        Raises:
            ValueError: If media_type is not supported
            aiohttp.ClientError: If message sending fails
        """
        # Remove + from phone number if present
        number = to.lstrip('+')
        
        # Supported media types
        supported_types = ["image", "video", "audio", "document"]
        
        if media_type not in supported_types:
            raise ValueError(
                f"Unsupported media_type: {media_type}. "
                f"Supported types: {', '.join(supported_types)}"
            )
        
        # Auto-detect MIME type if not provided
        if not mime_type:
            mime_map = {
                "image": "image/png",
                "video": "video/mp4",
                "audio": "audio/ogg",
                "document": "application/pdf"
            }
            mime_type = mime_map.get(media_type, "application/octet-stream")
        
        endpoint = f"/message/sendMedia/{self.instance_name}"
        payload = {
            "number": number,
            "mediatype": media_type,
            "mimetype": mime_type,
            "media": media_url
        }
        
        if caption:
            payload["caption"] = caption
        
        if file_name:
            payload["fileName"] = file_name
        
        logger.info(f"Sending {media_type} message to {to}")
        return await self._make_request("POST", endpoint, payload)
    
    async def get_instance_status(self) -> Dict[str, Any]:
        """
        Get WhatsApp instance connection status.
        
        Returns:
            Dict containing instance status information
            
        Raises:
            aiohttp.ClientError: If status check fails
        """
        endpoint = f"/instance/connectionState/{self.instance_name}"
        
        logger.info(f"Checking instance status: {self.instance_name}")
        return await self._make_request("GET", endpoint)
    
    async def setup_webhook(
        self,
        webhook_url: str,
        webhook_by_events: bool = True,
        webhook_base64: bool = False,
        events: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Configure webhook URL for receiving messages.
        
        Args:
            webhook_url: URL where webhooks will be sent
            webhook_by_events: If True, sends separate requests per event
            webhook_base64: If True, sends files in base64 format
            events: List of events to subscribe to (uses defaults if None)
            
        Returns:
            Dict containing webhook configuration status
            
        Raises:
            aiohttp.ClientError: If webhook setup fails
        """
        if events is None:
            events = [
                "QRCODE_UPDATED",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE"
            ]
        
        endpoint = f"/webhook/set/{self.instance_name}"
        payload = {
            "enabled": True,
            "url": webhook_url,
            "webhookByEvents": webhook_by_events,
            "webhookBase64": webhook_base64,
            "events": events
        }
        
        logger.info(f"Setting up webhook: {webhook_url}")
        return await self._make_request("POST", endpoint, payload)
    
    async def delete_message(
        self,
        message_id: str,
        to: str
    ) -> Dict[str, Any]:
        """
        Delete a message.
        
        Args:
            message_id: ID of the message to delete
            to: Phone number of the chat where message exists
            
        Returns:
            Dict containing deletion status
            
        Raises:
            aiohttp.ClientError: If deletion fails
        """
        # Remove + from phone number if present
        number = to.lstrip('+')
        
        endpoint = f"/message/delete/{self.instance_name}"
        payload = {
            "id": message_id,
            "remoteJid": f"{number}@s.whatsapp.net"
        }
        
        logger.info(f"Deleting message {message_id}")
        return await self._make_request("DELETE", endpoint, payload)
    
    async def send_reaction(
        self,
        message_id: str,
        to: str,
        emoji: str,
        from_me: bool = False
    ) -> Dict[str, Any]:
        """
        Send reaction to a message.
        
        Args:
            message_id: ID of the message to react to
            to: Phone number of the chat
            emoji: Emoji to react with
            from_me: Whether the message was sent by you
            
        Returns:
            Dict containing reaction status
            
        Raises:
            aiohttp.ClientError: If reaction fails
        """
        # Remove + from phone number if present
        number = to.lstrip('+')
        
        endpoint = f"/message/sendReaction/{self.instance_name}"
        payload = {
            "key": {
                "remoteJid": f"{number}@s.whatsapp.net",
                "fromMe": from_me,
                "id": message_id
            },
            "reaction": emoji
        }
        
        logger.info(f"Sending reaction {emoji} to message {message_id}")
        return await self._make_request("POST", endpoint, payload)
    
    async def get_profile_picture(self, phone: str) -> Dict[str, Any]:
        """
        Get profile picture URL for a phone number.
        
        Args:
            phone: Phone number to get profile picture for
            
        Returns:
            Dict containing profile picture URL
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        # Remove + from phone number if present
        number = phone.lstrip('+')
        
        endpoint = f"/chat/fetchProfilePictureUrl/{self.instance_name}"
        payload = {
            "number": number
        }
        
        logger.info(f"Fetching profile picture for {phone}")
        return await self._make_request("POST", endpoint, payload)
    
    async def close(self):
        """
        Close HTTP session and cleanup resources.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Evolution API session closed")
