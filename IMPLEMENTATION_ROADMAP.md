# WhatsSynergy - Implementation Roadmap
## Step-by-Step Development Tasks

**Project:** WhatsSynergy WhatsApp Bot Framework  
**Date:** October 8, 2025  
**Purpose:** Complete task list for building the project from scratch

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Phase 1: Library (`whatsapi-python`)](#phase-1-library-whatsapi-python)
3. [Phase 2: Application Core (`WhatsSynergy`)](#phase-2-application-core-whatssynergy)
4. [Phase 3: Plugin System](#phase-3-plugin-system)
5. [Phase 4: Database Layer](#phase-4-database-layer)
6. [Phase 5: Example Plugins](#phase-5-example-plugins)
7. [Phase 6: Testing & Documentation](#phase-6-testing--documentation)
8. [Task Dependencies](#task-dependencies)

---

## 🎯 Project Overview

### Architecture Summary
```
📦 whatsapi-python (Library)
   ↓ used by
🤖 WhatsSynergy (Application)
   ↓ loads
📝 Plugins (Your business logic)
```

### Key Technologies
- **Language:** Python 3.9+
- **Web Framework:** FastAPI
- **Database:** SQLModel (SQLite/PostgreSQL)
- **WhatsApp Provider:** Evolution API
- **Async:** asyncio, aiohttp

### Design Principles
- Separation of library (protocol) and application (bot)
- Modular database (each plugin manages its tables)
- Automatic plugin loading with dependency resolution
- Decorator-based handler registration

---

## 📦 Phase 1: Library (`whatsapi-python`)

### Goal
Create a reusable Python library for WhatsApp communication via Evolution API.

---

### Task 1.1: Project Setup - Library
**Priority:** HIGH  
**Estimated Time:** 30 minutes

**Description:**  
Set up the basic structure for the `whatsapi-python` library.

**Requirements:**
- Create separate repository/folder: `whatsapi-python/`
- Set up Python package structure
- Configure `setup.py` or `pyproject.toml` for pip installation

**Deliverables:**
```
whatsapi-python/
├── setup.py (or pyproject.toml)
├── README.md
├── LICENSE
├── .gitignore
└── whatsapi/
    ├── __init__.py
    ├── providers/
    │   └── __init__.py
    ├── models/
    │   └── __init__.py
    └── webhook/
        └── __init__.py
```

**Acceptance Criteria:**
- [ ] Package installable with `pip install -e .`
- [ ] Basic `__init__.py` exports work
- [ ] README with library description

**Dependencies:** None

**Reference:** See DESIGN_UNIFIED.md sections "מהי WhatsSynergy?" and "הספריה vs האפליקציה"

---

### Task 1.2: Base Provider Interface
**Priority:** HIGH  
**Estimated Time:** 1 hour

**Description:**  
Create the abstract base class for WhatsApp providers using the Adapter pattern.

**Requirements:**
- Define `WhatsAppProvider` abstract base class
- Specify all methods providers must implement
- Add proper type hints
- Include docstrings

**File:** `whatsapi/providers/base.py`

**Code Structure:**
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class WhatsAppProvider(ABC):
    """Abstract base class for WhatsApp providers"""
    
    @abstractmethod
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message"""
        pass
    
    @abstractmethod
    async def send_media_message(
        self, 
        to: str, 
        media_url: str, 
        media_type: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send media message (image/video/audio/document)"""
        pass
    
    @abstractmethod
    async def get_instance_status(self) -> Dict[str, Any]:
        """Get WhatsApp instance connection status"""
        pass
    
    @abstractmethod
    async def setup_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Configure webhook URL for receiving messages"""
        pass
```

**Acceptance Criteria:**
- [ ] Abstract class with all required methods
- [ ] Type hints on all parameters and returns
- [ ] Comprehensive docstrings
- [ ] No implementation details (pure interface)

**Dependencies:** Task 1.1

**Reference:** DESIGN_UNIFIED.md - "Communication Layer"

---

### Task 1.3: Message Models
**Priority:** HIGH  
**Estimated Time:** 1.5 hours

**Description:**  
Create data models for WhatsApp messages using dataclasses or Pydantic.

**Requirements:**
- Create `WhatsAppMessage` dataclass
- Create message type enums
- Create direction enum (incoming/outgoing)
- Support all message types (text, image, video, audio, document, location, contact, sticker)

**File:** `whatsapi/models/message.py`

**Code Structure:**
```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

class MessageType(str, Enum):
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
    INCOMING = "incoming"
    OUTGOING = "outgoing"

@dataclass
class WhatsAppMessage:
    """Normalized WhatsApp message model"""
    message_id: str
    from_number: str
    to_number: Optional[str]
    message_type: MessageType
    direction: MessageDirection
    timestamp: datetime
    
    # Content
    text: Optional[str] = None
    caption: Optional[str] = None
    
    # Media
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None
    media_size: Optional[int] = None
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Contact
    contact_vcard: Optional[str] = None
    
    # Metadata
    quoted_message_id: Optional[str] = None
    is_group: bool = False
    group_id: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
```

**Acceptance Criteria:**
- [ ] All message types supported
- [ ] Type hints complete
- [ ] Serialization to dict works
- [ ] Can be created from dict

**Dependencies:** Task 1.1

**Reference:** DESIGN_UNIFIED.md - "Message Processing Layer"

---

### Task 1.4: Evolution API Provider Implementation
**Priority:** HIGH  
**Estimated Time:** 3 hours

**Description:**  
Implement the Evolution API provider with all required methods.

**Requirements:**
- Implement `EvolutionAPIProvider` class
- Handle HTTP requests with aiohttp
- Implement all base provider methods
- Add error handling
- Add retry logic for failed requests
- Support authentication

**File:** `whatsapi/providers/evolution.py`

**Code Structure:**
```python
import aiohttp
from typing import Dict, Any, Optional
from .base import WhatsAppProvider

class EvolutionAPIProvider(WhatsAppProvider):
    """Evolution API provider implementation"""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        instance_name: str,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"apikey": self.api_key},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session
    
    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message via Evolution API"""
        session = await self._get_session()
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        payload = {
            "number": to,
            "text": text
        }
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    # Implement other methods...
```

**Acceptance Criteria:**
- [ ] All abstract methods implemented
- [ ] Successful API calls to Evolution API
- [ ] Error handling with custom exceptions
- [ ] Session management (reuse connections)
- [ ] Proper cleanup (close session)

**Dependencies:** Task 1.2

**Reference:** DESIGN_UNIFIED.md - "Evolution API & Adapter"

---

### Task 1.5: Webhook Handler
**Priority:** HIGH  
**Estimated Time:** 2 hours

**Description:**  
Create webhook parser to convert Evolution API webhooks to WhatsAppMessage objects.

**Requirements:**
- Parse Evolution API webhook JSON
- Extract phone numbers from JID format
- Detect message type automatically
- Handle all message types
- Validation and error handling

**File:** `whatsapi/webhook/handler.py`

**Code Structure:**
```python
from typing import Dict, Any, Optional
from datetime import datetime
from ..models.message import WhatsAppMessage, MessageType, MessageDirection

class WebhookHandler:
    """Parse Evolution API webhooks"""
    
    @staticmethod
    def parse(webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """
        Parse Evolution API webhook to WhatsAppMessage
        
        Args:
            webhook_data: Raw webhook JSON from Evolution API
            
        Returns:
            WhatsAppMessage object or None if invalid
        """
        try:
            # Validate
            if not WebhookHandler._validate(webhook_data):
                return None
            
            # Extract data
            event = webhook_data.get("event")
            data = webhook_data.get("data", {})
            
            # Handle different event types
            if event == "messages.upsert":
                return WebhookHandler._parse_message(data)
            
            return None
            
        except Exception as e:
            # Log error
            return None
    
    @staticmethod
    def _validate(data: Dict[str, Any]) -> bool:
        """Validate webhook structure"""
        return "event" in data and "data" in data
    
    @staticmethod
    def _parse_message(data: Dict[str, Any]) -> WhatsAppMessage:
        """Parse message data"""
        key = data.get("key", {})
        message = data.get("message", {})
        
        # Extract phone
        from_jid = key.get("remoteJid", "")
        from_number = WebhookHandler._extract_phone(from_jid)
        
        # Detect type
        message_type = WebhookHandler._detect_type(message)
        
        # Extract text
        text = WebhookHandler._extract_text(message, message_type)
        
        return WhatsAppMessage(
            message_id=key.get("id", ""),
            from_number=from_number,
            to_number=None,
            message_type=message_type,
            direction=MessageDirection.INCOMING,
            timestamp=datetime.now(),
            text=text,
            raw_data=data
        )
    
    @staticmethod
    def _extract_phone(jid: str) -> str:
        """Extract phone from JID format"""
        # 972501234567@s.whatsapp.net -> +972501234567
        phone = jid.split("@")[0]
        return f"+{phone}" if not phone.startswith("+") else phone
    
    @staticmethod
    def _detect_type(message: Dict[str, Any]) -> MessageType:
        """Detect message type from message object"""
        if "conversation" in message or "extendedTextMessage" in message:
            return MessageType.TEXT
        elif "imageMessage" in message:
            return MessageType.IMAGE
        elif "videoMessage" in message:
            return MessageType.VIDEO
        elif "audioMessage" in message:
            return MessageType.AUDIO
        elif "documentMessage" in message:
            return MessageType.DOCUMENT
        # Add more types...
        return MessageType.UNKNOWN
    
    @staticmethod
    def _extract_text(message: Dict[str, Any], msg_type: MessageType) -> Optional[str]:
        """Extract text content"""
        if msg_type == MessageType.TEXT:
            return (
                message.get("conversation") or
                message.get("extendedTextMessage", {}).get("text")
            )
        return None
```

**Acceptance Criteria:**
- [ ] Parses all message types correctly
- [ ] Phone number extraction works
- [ ] Handles malformed webhooks gracefully
- [ ] Returns None for invalid data
- [ ] Unit tests pass

**Dependencies:** Task 1.3

**Reference:** DESIGN_UNIFIED.md - "Message Handler"

---

### Task 1.6: Library Configuration & Packaging
**Priority:** MEDIUM  
**Estimated Time:** 1 hour

**Description:**  
Finalize library configuration for distribution.

**Requirements:**
- Complete `setup.py` or `pyproject.toml`
- Add version management
- Configure dependencies
- Add CLI examples in README
- Add license

**File:** `setup.py`

**Code Structure:**
```python
from setuptools import setup, find_packages

setup(
    name="whatsapi-python",
    version="1.0.0",
    description="Python library for WhatsApp communication via Evolution API",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.9.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

**Acceptance Criteria:**
- [ ] `pip install .` works
- [ ] All dependencies listed
- [ ] Version accessible via `whatsapi.__version__`
- [ ] README with usage examples

**Dependencies:** Tasks 1.1-1.5

**Reference:** DESIGN_UNIFIED.md - "שימוש בספריה בלבד"

---

## 🤖 Phase 2: Application Core (`WhatsSynergy`)

### Goal
Create the bot application that uses the library.

---

### Task 2.1: Project Setup - Application
**Priority:** HIGH  
**Estimated Time:** 30 minutes

**Description:**  
Set up the WhatsSynergy application structure.

**Requirements:**
- Create application directory structure
- Set up virtual environment
- Create requirements.txt
- Create .env.example
- Create basic README

**Deliverables:**
```
WhatsSynergy/
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── bot.py
│   ├── config.py
│   ├── handlers/
│   │   └── __init__.py
│   ├── filters/
│   │   └── __init__.py
│   └── database/
│       └── __init__.py
├── plugins/
│   └── .gitkeep
└── database/
    └── .gitkeep
```

**requirements.txt:**
```
whatsapi-python>=1.0.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
python-dotenv>=1.0.0
```

**.env.example:**
```
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=your_key_here
WHATSAPP_INSTANCE=my_bot
WEBHOOK_URL=https://yourdomain.com/webhook
DATABASE_URL=sqlite:///database/bot.db
```

**Acceptance Criteria:**
- [ ] Clean directory structure
- [ ] All dependencies installable
- [ ] .env.example documented
- [ ] README with setup instructions

**Dependencies:** Phase 1 complete

**Reference:** DESIGN_UNIFIED.md - "מבנה הפרויקטים"

---

### Task 2.2: Configuration Management
**Priority:** HIGH  
**Estimated Time:** 45 minutes

**Description:**  
Create configuration system using Pydantic Settings.

**Requirements:**
- Load from .env file
- Type validation
- Default values
- Environment-specific configs

**File:** `app/config.py`

**Code Structure:**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Evolution API
    evolution_api_url: str
    evolution_api_key: str
    whatsapp_instance: str
    webhook_url: str
    
    # Database
    database_url: str = "sqlite:///database/bot.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # or "text"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
```

**Acceptance Criteria:**
- [ ] Loads from .env
- [ ] Type validation works
- [ ] Missing required vars raise error
- [ ] Can access via `settings.evolution_api_url`

**Dependencies:** Task 2.1

**Reference:** DESIGN_UNIFIED.md - "Infrastructure Layer"

---

### Task 2.3: Filter System
**Priority:** HIGH  
**Estimated Time:** 2 hours

**Description:**  
Create the filter system for message routing.

**Requirements:**
- Base `Filter` class
- Built-in filters (text, image, command, private, group)
- Composable filters (AND, OR, NOT)
- FilterResult with data extraction

**File:** `app/filters/base.py`

**Code Structure:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
from whatsapi import WhatsAppMessage

@dataclass
class FilterResult:
    """Result of filter check"""
    passed: bool
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

class Filter(ABC):
    """Base filter class"""
    
    @abstractmethod
    async def __call__(self, message: WhatsAppMessage) -> FilterResult:
        """Check if message passes filter"""
        pass
    
    def __and__(self, other: 'Filter') -> 'AndFilter':
        """Combine filters with AND"""
        return AndFilter(self, other)
    
    def __or__(self, other: 'Filter') -> 'OrFilter':
        """Combine filters with OR"""
        return OrFilter(self, other)
    
    def __invert__(self) -> 'NotFilter':
        """Invert filter"""
        return NotFilter(self)

class AndFilter(Filter):
    """Combine two filters with AND"""
    def __init__(self, left: Filter, right: Filter):
        self.left = left
        self.right = right
    
    async def __call__(self, message: WhatsAppMessage) -> FilterResult:
        left_result = await self.left(message)
        if not left_result.passed:
            return FilterResult(passed=False)
        
        right_result = await self.right(message)
        if not right_result.passed:
            return FilterResult(passed=False)
        
        # Merge data
        data = {**left_result.data, **right_result.data}
        return FilterResult(passed=True, data=data)

# Similar for OrFilter, NotFilter
```

**File:** `app/filters/builtin.py`

**Code Structure:**
```python
from whatsapi import WhatsAppMessage, MessageType
from .base import Filter, FilterResult
from typing import Union, List

class TextFilter(Filter):
    """Filter for text messages"""
    async def __call__(self, message: WhatsAppMessage) -> FilterResult:
        passed = message.message_type == MessageType.TEXT
        return FilterResult(passed=passed)

class CommandFilter(Filter):
    """Filter for commands (messages starting with /)"""
    def __init__(self, commands: Union[str, List[str], None] = None):
        if isinstance(commands, str):
            self.commands = [commands]
        else:
            self.commands = commands
    
    async def __call__(self, message: WhatsAppMessage) -> FilterResult:
        if not message.text or not message.text.startswith("/"):
            return FilterResult(passed=False)
        
        parts = message.text.split(maxsplit=1)
        command = parts[0][1:]  # Remove /
        args = parts[1] if len(parts) > 1 else ""
        
        # If specific commands specified, check match
        if self.commands and command not in self.commands:
            return FilterResult(passed=False)
        
        return FilterResult(
            passed=True,
            data={"command": command, "args": args}
        )

class PrivateFilter(Filter):
    """Filter for private (non-group) messages"""
    async def __call__(self, message: WhatsAppMessage) -> FilterResult:
        return FilterResult(passed=not message.is_group)

# Add more filters...
```

**File:** `app/filters/__init__.py`

```python
from .base import Filter, FilterResult
from .builtin import (
    TextFilter,
    CommandFilter,
    PrivateFilter,
    GroupFilter,
    ImageFilter,
    VideoFilter,
    AudioFilter,
    DocumentFilter,
)

class Filters:
    """Namespace for built-in filters"""
    text = TextFilter()
    private = PrivateFilter()
    group = GroupFilter()
    image = ImageFilter()
    video = VideoFilter()
    audio = AudioFilter()
    document = DocumentFilter()
    
    @staticmethod
    def command(commands=None):
        return CommandFilter(commands)

# Global instance
filters = Filters()
```

**Acceptance Criteria:**
- [ ] All built-in filters work
- [ ] Composition (AND, OR, NOT) works
- [ ] Data extraction in FilterResult
- [ ] Type hints complete

**Dependencies:** Task 2.1

**Reference:** DESIGN_UNIFIED.md - "מערכת הפילטרים"

---

### Task 2.4: Bot Class - Handler Registry
**Priority:** HIGH  
**Estimated Time:** 2.5 hours

**Description:**  
Create the main Bot class with decorator-based handler registration.

**Requirements:**
- Decorator `@Bot.on_message(filter)`
- Static handler registry (unbound handlers)
- Instance handler adoption
- Handler execution with error isolation

**File:** `app/bot.py`

**Code Structure:**
```python
from typing import Callable, List, Dict, Any
from whatsapi import WhatsAppProvider, WhatsAppMessage
from .filters import Filter
import logging

logger = logging.getLogger(__name__)

# Global unbound handlers (before Bot instance created)
_UNBOUND_HANDLERS: List[Dict[str, Any]] = []

class Bot:
    """Main bot class"""
    
    def __init__(self, provider: WhatsAppProvider):
        self.provider = provider
        self.handlers: List[Dict[str, Any]] = []
        self.loaded_plugins: Dict[str, Any] = {}
        
        # Adopt unbound handlers
        self._adopt_handlers()
    
    def _adopt_handlers(self):
        """Adopt handlers from global registry"""
        for handler_info in _UNBOUND_HANDLERS:
            self.handlers.append({
                "handler": handler_info["handler"],
                "filter": handler_info["filter"],
                "name": handler_info["name"]
            })
        logger.info(f"Adopted {len(self.handlers)} handlers")
    
    @staticmethod
    def on_message(filter_obj: Filter):
        """
        Decorator to register message handler
        
        Usage:
            @Bot.on_message(filters.command("start"))
            async def start_handler(client: Bot, message: WhatsAppMessage):
                await client.provider.send_text_message(...)
        """
        def decorator(func: Callable):
            # Add to global registry
            _UNBOUND_HANDLERS.append({
                "handler": func,
                "filter": filter_obj,
                "name": func.__name__
            })
            logger.debug(f"Registered handler: {func.__name__}")
            return func
        return decorator
    
    async def process_message(self, message: WhatsAppMessage):
        """Process incoming message through handlers"""
        logger.info(f"Processing message from {message.from_number}")
        
        for handler_info in self.handlers:
            try:
                # Check filter
                filter_result = await handler_info["filter"](message)
                
                if filter_result.passed:
                    logger.info(f"Handler matched: {handler_info['name']}")
                    
                    # Execute handler
                    await handler_info["handler"](self, message)
                    
                    # Stop after first match
                    break
                    
            except Exception as e:
                logger.error(
                    f"Error in handler {handler_info['name']}: {e}",
                    exc_info=True
                )
                # Continue to next handler (error isolation)
                continue
        else:
            logger.debug("No handler matched")
```

**Acceptance Criteria:**
- [ ] Decorator registration works
- [ ] Handlers execute on matching messages
- [ ] Error in one handler doesn't affect others
- [ ] First matching handler stops chain
- [ ] Logging comprehensive

**Dependencies:** Tasks 2.1, 2.3

**Reference:** DESIGN_UNIFIED.md - "Bot Interface"

---

### Task 2.5: Plugin Loader
**Priority:** HIGH  
**Estimated Time:** 3 hours

**Description:**  
Create automatic plugin discovery and loading with dependency resolution.

**Requirements:**
- Discover plugins automatically
- Parse plugin metadata
- Topological sort for dependencies
- Load in correct order
- Call init_plugin() if exists

**File:** `app/bot.py` (add methods to Bot class)

**Code Structure:**
```python
# Add to Bot class

import importlib
from pathlib import Path
from typing import List, Dict

def load_plugins(self, plugins_dir: str):
    """
    Load plugins automatically with dependency resolution
    
    Args:
        plugins_dir: Path to plugins directory
    """
    logger.info(f"Loading plugins from {plugins_dir}")
    
    plugins_path = Path(plugins_dir)
    
    # 1. Discover
    discovered = self._discover_plugins(plugins_path)
    logger.info(f"Discovered {len(discovered)} plugins")
    
    # 2. Sort by dependencies
    sorted_plugins = self._sort_by_dependencies(discovered)
    
    # 3. Load
    for plugin_name in sorted_plugins:
        self._load_plugin(plugin_name, discovered[plugin_name])
    
    logger.info(f"✅ Loaded {len(self.loaded_plugins)} plugins")

def _discover_plugins(self, plugins_path: Path) -> Dict[str, Dict]:
    """Discover all plugins in directory"""
    plugins = {}
    
    for item in plugins_path.iterdir():
        if not item.is_dir() or not (item / "__init__.py").exists():
            continue
        
        try:
            # Import plugin module
            plugin_module = importlib.import_module(f"plugins.{item.name}")
            
            # Extract metadata
            plugins[item.name] = {
                "name": getattr(plugin_module, "PLUGIN_NAME", item.name),
                "version": getattr(plugin_module, "PLUGIN_VERSION", "1.0.0"),
                "dependencies": getattr(plugin_module, "PLUGIN_DEPENDENCIES", []),
                "has_database": getattr(plugin_module, "PLUGIN_HAS_DATABASE", False),
                "module": plugin_module,
                "path": item
            }
            
        except Exception as e:
            logger.error(f"Failed to discover plugin {item.name}: {e}")
            continue
    
    return plugins

def _sort_by_dependencies(self, plugins: Dict) -> List[str]:
    """
    Sort plugins by dependencies using topological sort
    
    Returns:
        List of plugin names in load order
    """
    sorted_list = []
    visited = set()
    visiting = set()  # For cycle detection
    
    def visit(name: str):
        if name in visited:
            return
        
        if name in visiting:
            raise ValueError(f"Circular dependency detected: {name}")
        
        plugin = plugins.get(name)
        if not plugin:
            raise ValueError(f"Plugin '{name}' not found but required as dependency")
        
        visiting.add(name)
        
        # Visit dependencies first
        for dep in plugin["dependencies"]:
            visit(dep)
        
        visiting.remove(name)
        visited.add(name)
        sorted_list.append(name)
    
    # Visit all plugins
    for plugin_name in plugins:
        visit(plugin_name)
    
    return sorted_list

def _load_plugin(self, plugin_name: str, plugin_info: Dict):
    """Load a single plugin"""
    try:
        module = plugin_info["module"]
        
        # Call init_plugin if exists
        if hasattr(module, "init_plugin"):
            from app.database import db
            module.init_plugin(db)
        
        # Import handlers (triggers @Bot.on_message decorators)
        try:
            importlib.import_module(f"plugins.{plugin_name}.handlers")
        except ImportError:
            logger.warning(f"Plugin {plugin_name} has no handlers.py")
        
        self.loaded_plugins[plugin_name] = module
        
        # Log
        deps = plugin_info["dependencies"]
        deps_str = f" (depends on: {', '.join(deps)})" if deps else ""
        logger.info(f"  📦 {plugin_info['name']} v{plugin_info['version']}{deps_str}")
        
    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_name}: {e}", exc_info=True)
```

**Acceptance Criteria:**
- [ ] Discovers all plugins automatically
- [ ] Parses metadata correctly
- [ ] Resolves dependencies (topological sort)
- [ ] Detects circular dependencies
- [ ] Logs loading process
- [ ] Error in one plugin doesn't stop others

**Dependencies:** Task 2.4

**Reference:** DESIGN_UNIFIED.md - "Plugin Loader אוטומטי"

---

### Task 2.6: Main Application Entry Point
**Priority:** HIGH  
**Estimated Time:** 1 hour

**Description:**  
Create the main.py entry point with FastAPI and webhook endpoint.

**Requirements:**
- Initialize FastAPI app
- Create webhook endpoint
- Initialize provider and bot
- Load plugins
- Run server

**File:** `main.py`

**Code Structure:**
```python
from fastapi import FastAPI, Request
from whatsapi import EvolutionAPIProvider, WebhookHandler
from app.bot import Bot
from app.config import settings
import logging
import uvicorn

# Logging setup
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="WhatsSynergy",
    description="WhatsApp Bot Framework",
    version="1.0.0"
)

# Initialize provider
provider = EvolutionAPIProvider(
    base_url=settings.evolution_api_url,
    api_key=settings.evolution_api_key,
    instance_name=settings.whatsapp_instance
)

# Initialize bot
bot = Bot(provider)

# Database initialization
from app.database import init_database
init_database(settings.database_url)

# Load plugins
bot.load_plugins("plugins")

# Create all tables
from app.database import db
db.create_tables()

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhooks from Evolution API"""
    try:
        data = await request.json()
        logger.debug(f"Webhook received: {data}")
        
        # Parse webhook
        message = WebhookHandler.parse(data)
        
        if message:
            # Process message
            await bot.process_message(message)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "plugins": len(bot.loaded_plugins)}

# Startup event
@app.on_event("startup")
async def startup():
    """Run on application startup"""
    logger.info("🚀 WhatsSynergy starting...")
    logger.info(f"📦 Loaded {len(bot.loaded_plugins)} plugins")
    logger.info(f"✅ Ready to receive webhooks at /webhook")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    """Run on application shutdown"""
    logger.info("Shutting down...")
    # Close provider session
    if hasattr(provider, '_session') and provider._session:
        await provider._session.close()

# Run
if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
```

**Acceptance Criteria:**
- [ ] Server starts successfully
- [ ] Webhook endpoint receives POST requests
- [ ] Health check works
- [ ] Plugins loaded on startup
- [ ] Graceful shutdown

**Dependencies:** Tasks 2.1-2.5

**Reference:** DESIGN_UNIFIED.md - "main.py"

---

## 📊 Phase 3: Plugin System

### Goal
Enable modular plugin architecture.

---

### Task 3.1: Plugin Structure Documentation
**Priority:** MEDIUM  
**Estimated Time:** 30 minutes

**Description:**  
Create documentation for plugin developers.

**Requirements:**
- Document plugin structure
- Document metadata fields
- Provide template
- Add examples

**File:** `PLUGIN_DEVELOPMENT.md`

**Content:**
```markdown
# Plugin Development Guide

## Plugin Structure

plugins/my_plugin/
├── __init__.py          # Metadata and init
├── handlers.py          # Message handlers
├── models.py            # Database models (optional)
└── repository.py        # Database operations (optional)

## Metadata (__init__.py)

PLUGIN_NAME = "my_plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DEPENDENCIES = []  # List of plugin names
PLUGIN_HAS_DATABASE = False

def init_plugin(db):
    # Called when plugin loads
    pass

## Handler Example

from app.bot import Bot
from app.filters import filters

@Bot.on_message(filters.command("hello"))
async def hello(client: Bot, message):
    await client.provider.send_text_message(
        message.from_number,
        "Hello!"
    )
```

**Acceptance Criteria:**
- [ ] Clear structure documented
- [ ] Examples provided
- [ ] Metadata explained
- [ ] Handler patterns shown

**Dependencies:** Task 2.5

**Reference:** DESIGN_UNIFIED.md - "מערכת הפלאגינים"

---

## 🗄️ Phase 4: Database Layer

### Goal
Implement modular database with SQLModel.

---

### Task 4.1: Core Database Setup
**Priority:** HIGH  
**Estimated Time:** 1.5 hours

**Description:**  
Create the core database infrastructure with SQLModel.

**Requirements:**
- CoreDB class with SQLModel
- Engine creation
- Session management
- Table creation

**File:** `app/database/core.py`

**Code Structure:**
```python
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

class CoreDB:
    """Core database manager"""
    
    def __init__(self, db_url: str):
        """
        Initialize database
        
        Args:
            db_url: Database URL (e.g., sqlite:///database/bot.db)
        """
        self.db_url = db_url
        
        # Create engine
        self.engine = create_engine(
            db_url,
            echo=False,  # Set True for SQL logging
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
        )
        
        logger.info(f"Database initialized: {db_url}")
    
    def create_tables(self):
        """Create all registered tables"""
        SQLModel.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        SQLModel.metadata.drop_all(self.engine)
        logger.warning("All tables dropped")

# Global database instance
db: CoreDB = None

def init_database(db_url: str):
    """Initialize global database"""
    global db
    db = CoreDB(db_url)
    return db

def get_session() -> Generator[Session, None, None]:
    """
    Get database session (for dependency injection)
    
    Usage:
        with get_session() as session:
            user = session.get(User, phone)
    """
    with db.get_session() as session:
        yield session
```

**File:** `app/database/__init__.py`

```python
from .core import CoreDB, db, init_database, get_session

__all__ = ["CoreDB", "db", "init_database", "get_session"]
```

**Acceptance Criteria:**
- [ ] Database initializes correctly
- [ ] Session management works
- [ ] Context manager pattern
- [ ] SQLite and PostgreSQL support

**Dependencies:** Task 2.1

**Reference:** DESIGN_UNIFIED.md - "Database Layer - מודולרי"

---

### Task 4.2: Plugin Database Models Documentation
**Priority:** MEDIUM  
**Estimated Time:** 30 minutes

**Description:**  
Document how plugins should define database models.

**Requirements:**
- Document SQLModel usage
- Show model examples
- Explain relationships
- Document repository pattern

**File:** `PLUGIN_DATABASE.md`

**Content:**
```markdown
# Plugin Database Guide

## Define Models (models.py)

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    phone: str = Field(primary_key=True)
    name: Optional[str] = None
    is_blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

## Initialize Plugin (__init__.py)

PLUGIN_HAS_DATABASE = True

def init_plugin(db):
    from .models import User
    # Model registered automatically

## Repository Pattern (repository.py)

from sqlmodel import Session, select
from .models import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_or_create(self, phone: str) -> User:
        user = self.session.exec(
            select(User).where(User.phone == phone)
        ).first()
        
        if not user:
            user = User(phone=phone)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        
        return user

## Usage in Handler

from app.database import get_session
from .repository import UserRepository

@Bot.on_message(filters.command("register"))
async def register(client, message):
    with get_session() as session:
        repo = UserRepository(session)
        user = repo.get_or_create(message.from_number)
    
    await client.provider.send_text_message(...)
```

**Acceptance Criteria:**
- [ ] SQLModel usage clear
- [ ] Repository pattern explained
- [ ] Examples complete
- [ ] Best practices included

**Dependencies:** Task 4.1

**Reference:** DESIGN_UNIFIED.md - "מבנה פלאגין עם Database"

---

## 📝 Phase 5: Example Plugins

### Goal
Create example plugins to demonstrate the framework.

---

### Task 5.1: Welcome Plugin (No Database)
**Priority:** MEDIUM  
**Estimated Time:** 30 minutes

**Description:**  
Simple welcome plugin without database.

**Structure:**
```
plugins/welcome/
├── __init__.py
└── handlers.py
```

**File:** `plugins/welcome/__init__.py`

```python
"""Welcome Plugin - Greets new users"""

PLUGIN_NAME = "welcome"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DEPENDENCIES = []
PLUGIN_HAS_DATABASE = False
```

**File:** `plugins/welcome/handlers.py`

```python
from app.bot import Bot
from app.filters import filters

@Bot.on_message(filters.command("start"))
async def start_command(client: Bot, message):
    """Handle /start command"""
    await client.provider.send_text_message(
        message.from_number,
        "👋 Welcome to WhatsSynergy!\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/help - Get help\n"
        "/ping - Test bot"
    )

@Bot.on_message(filters.command("help"))
async def help_command(client: Bot, message):
    """Handle /help command"""
    await client.provider.send_text_message(
        message.from_number,
        "📚 Help:\n\n"
        "This is a WhatsApp bot built with WhatsSynergy.\n"
        "Send /start to see available commands."
    )

@Bot.on_message(filters.command("ping"))
async def ping_command(client: Bot, message):
    """Handle /ping command"""
    await client.provider.send_text_message(
        message.from_number,
        "🏓 Pong!"
    )
```

**Acceptance Criteria:**
- [ ] Commands work correctly
- [ ] No database dependency
- [ ] Clean code structure

**Dependencies:** Phase 2 complete

**Reference:** DESIGN_UNIFIED.md - "פלאגין ללא Database"

---

### Task 5.2: Users Plugin (With Database)
**Priority:** MEDIUM  
**Estimated Time:** 1.5 hours

**Description:**  
User management plugin with database.

**Structure:**
```
plugins/users/
├── __init__.py
├── models.py
├── repository.py
└── handlers.py
```

**File:** `plugins/users/__init__.py`

```python
"""Users Plugin - Manage bot users"""

PLUGIN_NAME = "users"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DEPENDENCIES = []
PLUGIN_HAS_DATABASE = True

def init_plugin(db):
    """Initialize plugin with database"""
    from .models import User
    print(f"✅ Plugin '{PLUGIN_NAME}' loaded with database")
```

**File:** `plugins/users/models.py`

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    """User model"""
    __tablename__ = "users"
    
    phone: str = Field(primary_key=True)
    name: Optional[str] = None
    is_blocked: bool = False
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
```

**File:** `plugins/users/repository.py`

```python
from sqlmodel import Session, select
from .models import User
from datetime import datetime
from typing import Optional

class UserRepository:
    """User database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get(self, phone: str) -> Optional[User]:
        """Get user by phone"""
        return self.session.exec(
            select(User).where(User.phone == phone)
        ).first()
    
    def get_or_create(self, phone: str, name: str = None) -> User:
        """Get existing user or create new"""
        user = self.get(phone)
        
        if not user:
            user = User(phone=phone, name=name)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        
        return user
    
    def update_last_message(self, phone: str):
        """Update last message timestamp"""
        user = self.get(phone)
        if user:
            user.last_message_at = datetime.now()
            self.session.add(user)
            self.session.commit()
    
    def block(self, phone: str):
        """Block user"""
        user = self.get(phone)
        if user:
            user.is_blocked = True
            self.session.add(user)
            self.session.commit()
    
    def unblock(self, phone: str):
        """Unblock user"""
        user = self.get(phone)
        if user:
            user.is_blocked = False
            self.session.add(user)
            self.session.commit()
    
    def is_blocked(self, phone: str) -> bool:
        """Check if user is blocked"""
        user = self.get(phone)
        return user.is_blocked if user else False
    
    def count_users(self) -> int:
        """Count total users"""
        from sqlmodel import func
        return self.session.exec(
            select(func.count(User.phone))
        ).first()
```

**File:** `plugins/users/handlers.py`

```python
from app.bot import Bot
from app.filters import filters
from app.database import get_session
from .repository import UserRepository

@Bot.on_message(filters.command("register"))
async def register_command(client: Bot, message):
    """Register user"""
    with get_session() as session:
        repo = UserRepository(session)
        
        # Extract name from command args
        result = await filters.command("register")(message)
        name = result.data.get("args", "Unknown")
        
        # Get or create user
        user = repo.get_or_create(message.from_number, name=name)
    
    await client.provider.send_text_message(
        message.from_number,
        f"✅ Registered successfully!\n\n"
        f"Name: {user.name}\n"
        f"Phone: {user.phone}\n"
        f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}"
    )

@Bot.on_message(filters.command("stats"))
async def stats_command(client: Bot, message):
    """Show bot statistics"""
    with get_session() as session:
        repo = UserRepository(session)
        total = repo.count_users()
    
    await client.provider.send_text_message(
        message.from_number,
        f"📊 Bot Statistics:\n\n"
        f"Total Users: {total}"
    )

# Track all messages
@Bot.on_message(filters.text)
async def track_message(client: Bot, message):
    """Track user messages"""
    with get_session() as session:
        repo = UserRepository(session)
        repo.update_last_message(message.from_number)
```

**Acceptance Criteria:**
- [ ] Users stored in database
- [ ] Repository pattern used
- [ ] All operations work
- [ ] Handlers functional

**Dependencies:** Task 4.1, Phase 2

**Reference:** DESIGN_UNIFIED.md - "Plugin עם Database"

---

### Task 5.3: Analytics Plugin (With Dependencies)
**Priority:** LOW  
**Estimated Time:** 2 hours

**Description:**  
Analytics plugin that depends on users plugin.

**Structure:**
```
plugins/analytics/
├── __init__.py
├── models.py
├── repository.py
└── handlers.py
```

**File:** `plugins/analytics/__init__.py`

```python
"""Analytics Plugin - Track events and metrics"""

PLUGIN_NAME = "analytics"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DEPENDENCIES = ["users"]  # Depends on users plugin!
PLUGIN_HAS_DATABASE = True

def init_plugin(db):
    """Initialize plugin with database"""
    from .models import Event
    print(f"✅ Plugin '{PLUGIN_NAME}' loaded")
```

**File:** `plugins/analytics/models.py`

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Event(SQLModel, table=True):
    """Event tracking model"""
    __tablename__ = "analytics_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_phone: str = Field(foreign_key="users.phone")
    event_type: str
    event_data: Optional[str] = None  # JSON string
    timestamp: datetime = Field(default_factory=datetime.now)
```

**Acceptance Criteria:**
- [ ] Depends on users plugin
- [ ] Loads after users plugin
- [ ] Foreign key works
- [ ] Events tracked

**Dependencies:** Task 5.2

**Reference:** DESIGN_UNIFIED.md - "פלאגין עם תלויות"

---

## ✅ Phase 6: Testing & Documentation

### Goal
Ensure quality and completeness.

---

### Task 6.1: Unit Tests - Library
**Priority:** MEDIUM  
**Estimated Time:** 3 hours

**Description:**  
Write unit tests for the whatsapi-python library.

**Requirements:**
- Test WebhookHandler parsing
- Test message type detection
- Test phone extraction
- Test provider interface
- Mock Evolution API

**File:** `whatsapi-python/tests/test_webhook.py`

**Structure:**
```python
import pytest
from whatsapi.webhook import WebhookHandler
from whatsapi.models import WhatsAppMessage, MessageType

def test_parse_text_message():
    """Test parsing text message"""
    webhook_data = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "id": "123",
                "remoteJid": "972501234567@s.whatsapp.net"
            },
            "message": {
                "conversation": "Hello"
            }
        }
    }
    
    message = WebhookHandler.parse(webhook_data)
    
    assert message is not None
    assert message.from_number == "+972501234567"
    assert message.text == "Hello"
    assert message.message_type == MessageType.TEXT

# Add more tests...
```

**Acceptance Criteria:**
- [ ] 80%+ code coverage
- [ ] All message types tested
- [ ] Edge cases covered
- [ ] Tests pass

**Dependencies:** Phase 1 complete

---

### Task 6.2: Unit Tests - Application
**Priority:** MEDIUM  
**Estimated Time:** 3 hours

**Description:**  
Write unit tests for WhatsSynergy application.

**Requirements:**
- Test filter system
- Test handler registration
- Test plugin loading
- Test message routing

**File:** `tests/test_filters.py`

**Structure:**
```python
import pytest
from app.filters import filters, Filter, FilterResult
from whatsapi.models import WhatsAppMessage, MessageType
from datetime import datetime

@pytest.fixture
def text_message():
    """Create test text message"""
    return WhatsAppMessage(
        message_id="123",
        from_number="+972501234567",
        to_number=None,
        message_type=MessageType.TEXT,
        direction="incoming",
        timestamp=datetime.now(),
        text="/start"
    )

async def test_command_filter(text_message):
    """Test command filter"""
    result = await filters.command("start")(text_message)
    
    assert result.passed
    assert result.data["command"] == "start"
    assert result.data["args"] == ""

# Add more tests...
```

**Acceptance Criteria:**
- [ ] Filter tests comprehensive
- [ ] Handler registration tested
- [ ] Plugin loading tested
- [ ] All tests pass

**Dependencies:** Phase 2 complete

---

### Task 6.3: Integration Tests
**Priority:** LOW  
**Estimated Time:** 2 hours

**Description:**  
Write integration tests for end-to-end flows.

**Requirements:**
- Test webhook → handler flow
- Test database operations
- Test plugin interactions
- Mock Evolution API

**Acceptance Criteria:**
- [ ] Full flow tested
- [ ] Database in-memory for tests
- [ ] Mocked external calls
- [ ] Tests pass

**Dependencies:** Phases 1-5 complete

---

### Task 6.4: Documentation - README
**Priority:** HIGH  
**Estimated Time:** 1 hour

**Description:**  
Complete README files for both library and application.

**Requirements:**
- Clear project description
- Installation instructions
- Quick start guide
- Examples
- Links to full documentation

**Files:**
- `whatsapi-python/README.md`
- `WhatsSynergy/README.md`

**Acceptance Criteria:**
- [ ] Clear and concise
- [ ] Installation works
- [ ] Examples functional
- [ ] Links correct

**Dependencies:** All phases complete

---

### Task 6.5: API Documentation
**Priority:** MEDIUM  
**Estimated Time:** 2 hours

**Description:**  
Generate API documentation.

**Requirements:**
- Docstrings complete
- Sphinx or MkDocs setup
- Generate HTML docs
- Host documentation

**Acceptance Criteria:**
- [ ] All public APIs documented
- [ ] Examples in docstrings
- [ ] HTML docs generated
- [ ] Searchable

**Dependencies:** All phases complete

---

## 📊 Task Dependencies

### Dependency Graph

```
Phase 1 (Library)
├── 1.1 Project Setup
├── 1.2 Base Provider ← 1.1
├── 1.3 Message Models ← 1.1
├── 1.4 Evolution Provider ← 1.2
├── 1.5 Webhook Handler ← 1.3
└── 1.6 Packaging ← 1.1-1.5

Phase 2 (Application Core)
├── 2.1 Project Setup ← Phase 1
├── 2.2 Configuration ← 2.1
├── 2.3 Filter System ← 2.1
├── 2.4 Bot Class ← 2.1, 2.3
├── 2.5 Plugin Loader ← 2.4
└── 2.6 Main Entry ← 2.1-2.5

Phase 3 (Plugin System)
└── 3.1 Documentation ← 2.5

Phase 4 (Database)
├── 4.1 Core Database ← 2.1
└── 4.2 Documentation ← 4.1

Phase 5 (Example Plugins)
├── 5.1 Welcome Plugin ← Phase 2
├── 5.2 Users Plugin ← 4.1, Phase 2
└── 5.3 Analytics Plugin ← 5.2

Phase 6 (Testing & Docs)
├── 6.1 Library Tests ← Phase 1
├── 6.2 App Tests ← Phase 2
├── 6.3 Integration Tests ← Phases 1-5
├── 6.4 README ← All phases
└── 6.5 API Docs ← All phases
```

---

## 🎯 Priority Summary

### Critical Path (Must complete first)
1. Phase 1: Library (Tasks 1.1-1.5)
2. Phase 2: Application Core (Tasks 2.1-2.6)
3. Phase 4: Database (Task 4.1)
4. Phase 5: At least one plugin (Task 5.1 or 5.2)

### Can be done in parallel
- Task 3.1 (Plugin docs) while building Phase 5
- Task 4.2 (DB docs) while building Phase 5
- Phase 6 (Testing) incrementally throughout

### Lower priority
- Task 5.3 (Analytics plugin)
- Task 6.3 (Integration tests)
- Task 6.5 (API docs)

---

## 📝 Notes for AI Implementation

### When implementing each task:

1. **Always reference DESIGN_UNIFIED.md**
   - Check architecture section for context
   - Follow design patterns specified
   - Match code structure to examples

2. **Follow Python best practices**
   - Type hints on all functions
   - Docstrings with Args/Returns
   - PEP 8 style guide
   - Async/await properly

3. **Error handling**
   - Try-except blocks where needed
   - Proper logging
   - Graceful degradation
   - Don't crash the bot

4. **Testing mindset**
   - Write testable code
   - Avoid tight coupling
   - Use dependency injection
   - Mock external services

5. **Documentation**
   - Docstrings on all public APIs
   - Comments for complex logic
   - README for each component
   - Examples in docs

### Code Review Checklist

Before marking task complete:
- [ ] Code follows task requirements
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Tested manually
- [ ] Acceptance criteria met
- [ ] Referenced DESIGN_UNIFIED.md
- [ ] No hardcoded values
- [ ] Environment variables used

---

## 🚀 Getting Started

### For AI Assistants

To implement this project:

1. Read DESIGN_UNIFIED.md completely
2. Start with Phase 1, Task 1.1
3. Complete tasks in dependency order
4. Reference this roadmap for each task
5. Check acceptance criteria before moving on
6. Ask questions if requirements unclear

### For Humans

To assign tasks to AI:

1. Provide both DESIGN_UNIFIED.md and this file
2. Specify task number clearly (e.g., "Implement Task 2.4")
3. Confirm AI understands requirements
4. Review code against acceptance criteria
5. Test implementation before merging

---

**End of Implementation Roadmap**

*This roadmap should be used together with DESIGN_UNIFIED.md for complete context.*
