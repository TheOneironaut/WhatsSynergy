"""Webhook handler for parsing Evolution API webhooks"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..models.message import WhatsAppMessage, MessageType, MessageDirection

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Parse Evolution API webhooks into WhatsAppMessage objects.
    
    This handler converts raw webhook JSON from Evolution API into
    normalized WhatsAppMessage objects that are provider-agnostic.
    """
    
    @staticmethod
    def parse(webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """
        Parse Evolution API webhook to WhatsAppMessage.
        
        Args:
            webhook_data: Raw webhook JSON from Evolution API
            
        Returns:
            WhatsAppMessage object or None if invalid/unsupported
        """
        try:
            # Validate basic structure
            if not WebhookHandler._validate(webhook_data):
                logger.warning("Invalid webhook structure")
                return None
            
            event = webhook_data.get("event")
            data = webhook_data.get("data", {})
            
            # Handle different event types
            if event == "messages.upsert":
                return WebhookHandler._parse_message_upsert(data)
            elif event == "MESSAGES_UPSERT":
                return WebhookHandler._parse_message_upsert(data)
            else:
                logger.debug(f"Unsupported event type: {event}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _validate(data: Dict[str, Any]) -> bool:
        """
        Validate webhook structure.
        
        Args:
            data: Webhook data
            
        Returns:
            True if valid, False otherwise
        """
        return "event" in data and "data" in data
    
    @staticmethod
    def _parse_message_upsert(data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """
        Parse messages.upsert event.
        
        Args:
            data: Message data from webhook
            
        Returns:
            WhatsAppMessage object or None
        """
        try:
            key = data.get("key", {})
            message = data.get("message", {})
            message_timestamp = data.get("messageTimestamp")
            push_name = data.get("pushName", "")
            
            # Extract message ID
            message_id = key.get("id", "")
            if not message_id:
                logger.warning("Message ID not found")
                return None
            
            # Extract phone numbers
            remote_jid = key.get("remoteJid", "")
            from_me = key.get("fromMe", False)
            
            from_number = WebhookHandler._extract_phone(remote_jid)
            
            # Determine direction
            direction = MessageDirection.OUTGOING if from_me else MessageDirection.INCOMING
            
            # Check if group message
            is_group = "@g.us" in remote_jid
            group_id = remote_jid if is_group else None
            
            # Detect message type
            message_type = WebhookHandler._detect_type(message)
            
            # Extract content based on type
            text = None
            caption = None
            media_url = None
            media_mime_type = None
            media_size = None
            media_filename = None
            latitude = None
            longitude = None
            location_name = None
            location_address = None
            contact_vcard = None
            contact_name = None
            quoted_message_id = None
            quoted_message_text = None
            
            if message_type == MessageType.TEXT:
                text = WebhookHandler._extract_text(message)
                
                # Check for quoted message
                if "extendedTextMessage" in message:
                    ext_msg = message["extendedTextMessage"]
                    context_info = ext_msg.get("contextInfo", {})
                    if context_info:
                        quoted_message_id = context_info.get("stanzaId")
                        quoted_msg = context_info.get("quotedMessage", {})
                        if quoted_msg:
                            quoted_message_text = WebhookHandler._extract_text(quoted_msg)
            
            elif message_type == MessageType.IMAGE:
                img_msg = message.get("imageMessage", {})
                media_url = img_msg.get("url")
                media_mime_type = img_msg.get("mimetype")
                media_size = img_msg.get("fileLength")
                caption = img_msg.get("caption")
            
            elif message_type == MessageType.VIDEO:
                vid_msg = message.get("videoMessage", {})
                media_url = vid_msg.get("url")
                media_mime_type = vid_msg.get("mimetype")
                media_size = vid_msg.get("fileLength")
                caption = vid_msg.get("caption")
            
            elif message_type == MessageType.AUDIO:
                aud_msg = message.get("audioMessage", {})
                media_url = aud_msg.get("url")
                media_mime_type = aud_msg.get("mimetype")
                media_size = aud_msg.get("fileLength")
            
            elif message_type == MessageType.DOCUMENT:
                doc_msg = message.get("documentMessage", {})
                media_url = doc_msg.get("url")
                media_mime_type = doc_msg.get("mimetype")
                media_size = doc_msg.get("fileLength")
                media_filename = doc_msg.get("fileName")
                caption = doc_msg.get("caption")
            
            elif message_type == MessageType.STICKER:
                stk_msg = message.get("stickerMessage", {})
                media_url = stk_msg.get("url")
                media_mime_type = stk_msg.get("mimetype")
                media_size = stk_msg.get("fileLength")
            
            elif message_type == MessageType.LOCATION:
                loc_msg = message.get("locationMessage", {})
                latitude = loc_msg.get("degreesLatitude")
                longitude = loc_msg.get("degreesLongitude")
                location_name = loc_msg.get("name")
                location_address = loc_msg.get("address")
            
            elif message_type == MessageType.CONTACT:
                cont_msg = message.get("contactMessage", {})
                contact_vcard = cont_msg.get("vcard")
                contact_name = cont_msg.get("displayName")
            
            # Create timestamp
            if message_timestamp:
                timestamp = datetime.fromtimestamp(int(message_timestamp))
            else:
                timestamp = datetime.now()
            
            # Create message object
            return WhatsAppMessage(
                message_id=message_id,
                from_number=from_number,
                to_number=None,  # Not available in incoming messages
                message_type=message_type,
                direction=direction,
                timestamp=timestamp,
                text=text,
                caption=caption,
                media_url=media_url,
                media_mime_type=media_mime_type,
                media_size=media_size,
                media_filename=media_filename,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                location_address=location_address,
                contact_vcard=contact_vcard,
                contact_name=contact_name,
                quoted_message_id=quoted_message_id,
                quoted_message_text=quoted_message_text,
                is_group=is_group,
                group_id=group_id,
                sender_name=push_name if push_name else None,
                raw_data=data
            )
            
        except Exception as e:
            logger.error(f"Error parsing message upsert: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _extract_phone(jid: str) -> str:
        """
        Extract phone number from JID format.
        
        Args:
            jid: JID string (e.g., "972501234567@s.whatsapp.net")
            
        Returns:
            Phone number with + prefix (e.g., "+972501234567")
        """
        if not jid:
            return ""
        
        # Split by @ to get number part
        phone = jid.split("@")[0]
        
        # Add + prefix if not present
        if not phone.startswith("+"):
            phone = f"+{phone}"
        
        return phone
    
    @staticmethod
    def _detect_type(message: Dict[str, Any]) -> MessageType:
        """
        Detect message type from message object.
        
        Args:
            message: Message object from webhook
            
        Returns:
            MessageType enum value
        """
        if "conversation" in message:
            return MessageType.TEXT
        elif "extendedTextMessage" in message:
            return MessageType.TEXT
        elif "imageMessage" in message:
            return MessageType.IMAGE
        elif "videoMessage" in message:
            return MessageType.VIDEO
        elif "audioMessage" in message:
            return MessageType.AUDIO
        elif "documentMessage" in message:
            return MessageType.DOCUMENT
        elif "stickerMessage" in message:
            return MessageType.STICKER
        elif "locationMessage" in message:
            return MessageType.LOCATION
        elif "contactMessage" in message:
            return MessageType.CONTACT
        else:
            logger.debug(f"Unknown message type: {list(message.keys())}")
            return MessageType.UNKNOWN
    
    @staticmethod
    def _extract_text(message: Dict[str, Any]) -> Optional[str]:
        """
        Extract text content from message.
        
        Args:
            message: Message object
            
        Returns:
            Text content or None
        """
        # Simple text message
        if "conversation" in message:
            return message["conversation"]
        
        # Extended text message (links, quotes, etc.)
        if "extendedTextMessage" in message:
            return message["extendedTextMessage"].get("text")
        
        # Text in other message types
        if "text" in message:
            return message["text"]
        
        return None
