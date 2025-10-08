# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-08

### Added
- Initial release of whatsapi-python
- Evolution API provider implementation
- WhatsApp message models (WhatsAppMessage, MessageType, MessageDirection)
- Webhook handler for parsing Evolution API webhooks
- Support for all message types:
  - Text messages
  - Images
  - Videos
  - Audio
  - Documents
  - Stickers
  - Location
  - Contacts (vCard)
- Quoted message (reply) support
- Group message support
- Retry logic for failed requests
- Context manager support for provider
- Comprehensive error handling
- Full type hints
- Logging support
- Session management with automatic cleanup

### Features
- Async/await support with asyncio
- Automatic retry on failures
- Phone number normalization
- JID format handling
- Media message support with captions
- Message reactions
- Profile picture retrieval
- Instance status checking
- Webhook configuration
- Message deletion

### Documentation
- Complete README with examples
- API reference documentation
- Examples file with common use cases
- Inline docstrings for all public APIs
