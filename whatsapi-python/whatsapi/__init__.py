"""
whatsapi-python - WhatsApp communication library via Evolution API
"""

__version__ = "1.0.0"

from .providers.base import WhatsAppProvider
from .providers.evolution import EvolutionAPIProvider
from .models.message import WhatsAppMessage, MessageType, MessageDirection
from .webhook.handler import WebhookHandler

__all__ = [
    "WhatsAppProvider",
    "EvolutionAPIProvider",
    "WhatsAppMessage",
    "MessageType",
    "MessageDirection",
    "WebhookHandler",
]
