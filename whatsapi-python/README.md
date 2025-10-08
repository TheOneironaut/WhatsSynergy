# whatsapi-python

Python library for WhatsApp communication via Evolution API.

## Description

`whatsapi-python` is a reusable Python library that provides a clean interface for WhatsApp communication through the Evolution API. It uses the Adapter pattern to allow easy integration with different WhatsApp providers.

## Features

- 🔌 **Adapter Pattern**: Easy integration with different WhatsApp providers
- 📨 **Message Handling**: Support for all WhatsApp message types (text, media, location, contact, etc.)
- 🪝 **Webhook Processing**: Parse and normalize incoming webhooks
- ⚡ **Async Support**: Built with asyncio for high performance
- 🎯 **Type Hints**: Full type annotation for better IDE support
- 🔄 **Retry Logic**: Automatic retry on failed requests
- 🧹 **Resource Management**: Proper session cleanup

## Installation

### From source (development)

```bash
cd whatsapi-python
pip install -e .
```

### From PyPI (future)

```bash
pip install whatsapi-python
```

## Quick Start

### Sending Messages

```python
import asyncio
from whatsapi import EvolutionAPIProvider

async def main():
    # Initialize provider
    provider = EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot"
    )
    
    try:
        # Send text message
        await provider.send_text_message(
            to="+972501234567",
            text="Hello from whatsapi-python!"
        )
        
        # Send image
        await provider.send_media_message(
            to="+972501234567",
            media_url="https://example.com/image.jpg",
            media_type="image",
            caption="Check this out!"
        )
        
        # Check instance status
        status = await provider.get_instance_status()
        print(f"Instance status: {status}")
        
    finally:
        # Always close the provider
        await provider.close()

# Run
asyncio.run(main())
```

### Processing Webhooks

```python
from whatsapi import WebhookHandler

# Parse webhook from Evolution API
webhook_data = {...}  # Your webhook JSON
message = WebhookHandler.parse(webhook_data)

if message:
    print(f"From: {message.from_number}")
    print(f"Type: {message.message_type}")
    
    if message.is_text:
        print(f"Text: {message.text}")
    
    if message.is_media:
        print(f"Media URL: {message.media_url}")
    
    if message.is_group:
        print(f"Group: {message.group_id}")
```

### Using with Context Manager (Recommended)

```python
from whatsapi import EvolutionAPIProvider

async def send_message():
    async with EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot"
    ) as provider:
        await provider.send_text_message(
            to="+972501234567",
            text="Hello!"
        )
    # Provider automatically closed
```

## API Reference

### EvolutionAPIProvider

Main provider class for Evolution API integration.

**Methods:**
- `send_text_message(to, text)` - Send text message
- `send_media_message(to, media_url, media_type, caption)` - Send media
- `get_instance_status()` - Get connection status
- `setup_webhook(webhook_url)` - Configure webhook
- `delete_message(message_id, to)` - Delete message
- `send_reaction(message_id, to, emoji)` - React to message
- `get_profile_picture(phone)` - Get profile picture URL
- `close()` - Close HTTP session

### WebhookHandler

Parse Evolution API webhooks.

**Methods:**
- `parse(webhook_data)` - Parse webhook to WhatsAppMessage

### WhatsAppMessage

Normalized message object.

**Properties:**
- `message_id` - Unique message ID
- `from_number` - Sender phone number
- `message_type` - Type (text, image, video, etc.)
- `direction` - incoming or outgoing
- `text` - Text content
- `media_url` - Media file URL
- `is_group` - Boolean indicating group message
- `is_text` - Boolean property
- `is_media` - Boolean property
- `has_quoted_message` - Boolean property

## Supported Message Types

- ✅ Text messages
- ✅ Images
- ✅ Videos
- ✅ Audio
- ✅ Documents
- ✅ Stickers
- ✅ Location
- ✅ Contacts (vCard)
- ✅ Quoted messages (replies)
- ✅ Group messages

## Error Handling

The library uses proper exception handling and retry logic:

```python
from aiohttp import ClientError

try:
    await provider.send_text_message(to="+123", text="Hello")
except ClientError as e:
    print(f"Failed to send message: {e}")
```

## Requirements

- Python 3.9+
- aiohttp >= 3.9.0
- python-dotenv >= 1.0.0

## Supported Providers

- ✅ Evolution API

## Documentation

See [DESIGN_UNIFIED.md](../DESIGN_UNIFIED.md) for complete architecture documentation.

## Contributing

Contributions are welcome! Please read the contributing guidelines first.

## License

MIT License - see LICENSE file for details.

## Version

Current version: 1.0.0
