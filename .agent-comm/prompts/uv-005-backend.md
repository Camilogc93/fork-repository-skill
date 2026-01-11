# Task: Fix UTF-8 Encoding in message_bus.py

**Task ID**: uv-005
**Role**: Backend
**Priority**: P2 (Medium)
**Depends on**: uv-002

## Objective

Fix UTF-8 encoding issues in message_bus.py that cause errors on Windows when logging messages with unicode characters (like arrows →).

## File to Modify

`.claude/skills/fork-terminal/tools/message_bus.py`

## Problem

The `_log_message()` method (around line 421) writes to a log file without specifying encoding, causing:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'
```

## Fix Required

Update the `_log_message()` method:

```python
def _log_message(self, message: Message):
    """Log message to communications log."""
    log_entry = (
        f"[{message.timestamp}] "
        f"{message.from_agent} -> {message.to_agent} "  # Use ASCII arrow
        f"[{message.message_type.value}] "
        f"ID: {message.message_id}\n"
    )

    with open(self.log_file, 'a', encoding='utf-8') as f:  # Add encoding
        f.write(log_entry)
```

## Additional Fixes

1. Replace unicode arrow `→` with ASCII `->` in log entries
2. Add `encoding='utf-8'` to all file operations in the class
3. Check other methods that write files

## Verification

```python
from message_bus import MessageBus, MessageType
bus = MessageBus()
bus.send_message('test-from', 'test-to', MessageType.NOTIFICATION, {'msg': 'test'})
# Should not raise encoding error
```

## Success Criteria

- No UnicodeEncodeError on Windows
- Log file is UTF-8 encoded
- Messages can be sent without errors
