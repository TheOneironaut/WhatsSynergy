"""Base provider interface for WhatsApp communication"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class WhatsAppProvider(ABC):
    """
    Abstract base class for WhatsApp providers.
    
    This interface defines the contract that all WhatsApp providers must implement.
    Uses the Adapter pattern to allow integration with different WhatsApp APIs.
    """
    
    @abstractmethod
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Send a text message to a WhatsApp number.
        
        Args:
            to: Recipient phone number (e.g., "+972501234567")
            text: Message text content
            
        Returns:
            Dict containing the API response with message status
            
        Raises:
            Exception: If message sending fails
        """
        pass
    
    @abstractmethod
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
        Send a media message (image/video/audio/document).
        
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
            Exception: If message sending fails
        """
        pass
    
    @abstractmethod
    async def get_instance_status(self) -> Dict[str, Any]:
        """
        Get WhatsApp instance connection status.
        
        Returns:
            Dict containing instance status information (connected, qr_code, etc.)
            
        Raises:
            Exception: If status check fails
        """
        pass
    
    @abstractmethod
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
            events: List of events to subscribe to
            
        Returns:
            Dict containing webhook configuration status
            
        Raises:
            Exception: If webhook setup fails
        """
        pass
    
    @abstractmethod
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
            Exception: If deletion fails
        """
        pass
    
    async def close(self):
        """
        Close provider resources (e.g., HTTP sessions).
        
        Should be called when the provider is no longer needed.
        Default implementation does nothing.
        """
        pass
