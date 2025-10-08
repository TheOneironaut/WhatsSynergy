# Examples for whatsapi-python

This directory contains usage examples for the whatsapi-python library.

## Basic Examples

### 1. Simple Text Message

```python
import asyncio
from whatsapi import EvolutionAPIProvider

async def send_simple_message():
    provider = EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot"
    )
    
    try:
        result = await provider.send_text_message(
            to="+972501234567",
            text="Hello from WhatsApp Bot!"
        )
        print(f"Message sent: {result}")
    finally:
        await provider.close()

asyncio.run(send_simple_message())
```

### 2. Send Media with Caption

```python
import asyncio
from whatsapi import EvolutionAPIProvider

async def send_image():
    async with EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot"
    ) as provider:
        
        await provider.send_media_message(
            to="+972501234567",
            media_url="https://example.com/photo.jpg",
            media_type="image",
            caption="Check out this photo! 📸"
        )

asyncio.run(send_image())
```

### 3. Process Webhook

```python
from whatsapi import WebhookHandler
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    
    # Parse webhook
    message = WebhookHandler.parse(data)
    
    if message and message.is_text:
        print(f"Received: {message.text} from {message.from_number}")
    
    return {"status": "ok"}
```

### 4. Echo Bot

```python
import asyncio
from whatsapi import EvolutionAPIProvider, WebhookHandler
from fastapi import FastAPI, Request

app = FastAPI()

provider = EvolutionAPIProvider(
    base_url="http://localhost:8080",
    api_key="your_api_key",
    instance_name="my_bot"
)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = WebhookHandler.parse(data)
    
    if message and message.is_text and message.direction == "incoming":
        # Echo the message back
        await provider.send_text_message(
            to=message.from_number,
            text=f"You said: {message.text}"
        )
    
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown():
    await provider.close()
```

### 5. Check Instance Status

```python
import asyncio
from whatsapi import EvolutionAPIProvider

async def check_status():
    async with EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot"
    ) as provider:
        
        status = await provider.get_instance_status()
        print(f"Status: {status}")

asyncio.run(check_status())
```

### 6. Setup Webhook

```python
import asyncio
from whatsapi import EvolutionAPIProvider

async def setup_webhook():
    async with EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot"
    ) as provider:
        
        result = await provider.setup_webhook(
            webhook_url="https://yourdomain.com/webhook"
        )
        print(f"Webhook configured: {result}")

asyncio.run(setup_webhook())
```

## Advanced Examples

### Message Type Detection

```python
from whatsapi import WebhookHandler, MessageType

webhook_data = {...}  # Your webhook
message = WebhookHandler.parse(webhook_data)

if message:
    if message.message_type == MessageType.TEXT:
        print(f"Text: {message.text}")
    elif message.message_type == MessageType.IMAGE:
        print(f"Image URL: {message.media_url}")
        print(f"Caption: {message.caption}")
    elif message.message_type == MessageType.LOCATION:
        print(f"Location: {message.latitude}, {message.longitude}")
```

### Group Message Handling

```python
from whatsapi import WebhookHandler

message = WebhookHandler.parse(webhook_data)

if message and message.is_group:
    print(f"Group message from: {message.sender_name}")
    print(f"Group ID: {message.group_id}")
```

### Quoted Message (Reply)

```python
from whatsapi import WebhookHandler

message = WebhookHandler.parse(webhook_data)

if message and message.has_quoted_message:
    print(f"Replying to: {message.quoted_message_text}")
    print(f"Reply: {message.text}")
```

## Error Handling

```python
import asyncio
from whatsapi import EvolutionAPIProvider
from aiohttp import ClientError

async def safe_send():
    provider = EvolutionAPIProvider(
        base_url="http://localhost:8080",
        api_key="your_api_key",
        instance_name="my_bot",
        max_retries=3,
        timeout=30
    )
    
    try:
        await provider.send_text_message(
            to="+972501234567",
            text="Hello"
        )
    except ClientError as e:
        print(f"Failed to send: {e}")
    finally:
        await provider.close()

asyncio.run(safe_send())
```

## Using Environment Variables

```python
import os
from dotenv import load_dotenv
from whatsapi import EvolutionAPIProvider

load_dotenv()

provider = EvolutionAPIProvider(
    base_url=os.getenv("EVOLUTION_API_URL"),
    api_key=os.getenv("EVOLUTION_API_KEY"),
    instance_name=os.getenv("WHATSAPP_INSTANCE")
)
```
