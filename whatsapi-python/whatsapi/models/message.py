"""WhatsApp message models and types"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class MessageType(str, Enum):
    """WhatsApp message type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"
    STICKER = "sticker"
    UNKNOWN = "unknown"


class MessageDirection(str, Enum):
    """Message direction enumeration"""
    INCOMING = "incoming"
    OUTGOING = "outgoing"


@dataclass
class WhatsAppMessage:
    """
    Normalized WhatsApp message model.
    
    This class represents a WhatsApp message in a provider-agnostic format.
    It supports all message types and can be created from different provider formats.
    """
    
    # Required fields
    message_id: str
    from_number: str
    to_number: Optional[str]
    message_type: MessageType
    direction: MessageDirection
    timestamp: datetime
    
    # Text content
    text: Optional[str] = None
    caption: Optional[str] = None
    
    # Media fields
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None
    media_size: Optional[int] = None
    media_filename: Optional[str] = None
    
    # Location fields
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    
    # Contact fields
    contact_vcard: Optional[str] = None
    contact_name: Optional[str] = None
    
    # Message context
    quoted_message_id: Optional[str] = None
    quoted_message_text: Optional[str] = None
    
    # Group fields
    is_group: bool = False
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    
    # Sender info (for groups)
    sender_name: Optional[str] = None
    
    # Metadata
    raw_data: Optional[Dict[str, Any]] = field(default=None, repr=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary.
        
        Returns:
            Dictionary representation of the message
        """
        data = asdict(self)
        # Convert enums to strings
        data['message_type'] = self.message_type.value
        data['direction'] = self.direction.value
        # Convert datetime to ISO format
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WhatsAppMessage':
        """
        Create message from dictionary.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            WhatsAppMessage instance
        """
        # Convert string enums back to enum types
        if 'message_type' in data and isinstance(data['message_type'], str):
            data['message_type'] = MessageType(data['message_type'])
        if 'direction' in data and isinstance(data['direction'], str):
            data['direction'] = MessageDirection(data['direction'])
        # Convert ISO string to datetime
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
    
    @property
    def is_text(self) -> bool:
        """Check if message is text type"""
        return self.message_type == MessageType.TEXT
    
    @property
    def is_media(self) -> bool:
        """Check if message is media type"""
        return self.message_type in [
            MessageType.IMAGE,
            MessageType.VIDEO,
            MessageType.AUDIO,
            MessageType.DOCUMENT,
            MessageType.STICKER
        ]
    
    @property
    def has_quoted_message(self) -> bool:
        """Check if message is a reply to another message"""
        return self.quoted_message_id is not None
    
    def __str__(self) -> str:
        """String representation of message"""
        type_str = self.message_type.value
        from_str = self.from_number
        
        if self.is_text and self.text:
            preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
            return f"WhatsAppMessage({type_str} from {from_str}: {preview})"
        elif self.is_media:
            return f"WhatsAppMessage({type_str} from {from_str})"
        else:
            return f"WhatsAppMessage({type_str} from {from_str})"
