# effects-logging

A composable logging framework built on the [effects library](https://github.com/ludvb/effects).

## Installation

```bash
pip install git+https://github.com/ludvb/effects-logging.git
```

## Usage

```python
import effects_logging as logging
from effects_logging import text_writer

# Basic logging
with text_writer():
    logging.log_info("Application started")
    logging.log_error("Something went wrong")

# Progress bars
with text_writer():
    for item in logging.progressbar(range(100)):
        process(item)
```

## Features

### Structured Logging

```python
from effects_logging import log_debug, log_info, log_warning, log_error, text_writer

with text_writer():
    log_debug("Debug information")
    log_info("Application running")
    log_warning("Resource usage high")
    log_error("Connection failed")
```

### Progress Tracking

```python
# Basic progress bar
items = load_data()
with text_writer():
    for item in progressbar(items, initial_desc="Processing"):
        process(item)

# Dynamic descriptions
files = ["data.csv", "report.pdf", "image.png"]
with text_writer():
    for f in progressbar(files, desc_callback=lambda x: f"Processing {x}"):
        process_file(f)
```

### File Output

```python
# Write to file (progress bars automatically disabled)
with open("app.log", "w") as f:
    with text_writer(f):
        log_info("Writing to file")
        for i in progressbar(range(10)):
            log_info(f"Step {i}")

# Simultaneous console and file output
import sys
import effects as fx

with open("app.log", "w") as f:
    with text_writer(sys.stdout), text_writer(f):
        log_info("Goes to both console and file")
```

### Custom Handlers

The effects pattern allows you to compose and customize logging behavior:

```python
import os
import effects as fx
from effects_logging import LogMessage, log_info, text_writer

# Transform messages before they reach the output handler
def add_context(effect: LogMessage) -> None:
    """Add contextual information to all log messages."""
    modified = LogMessage(
        message=f"[{os.getpid()}] {effect.message}",
        level=effect.level
    )
    fx.send(modified, interpret_final=False)  # Forward modified effect

# Stack handlers - transformations run first, then output
with text_writer(), fx.handler(add_context, LogMessage):
    log_info("Server started")  # Output includes PID prefix

# Or completely replace the output format
def json_handler(effect: LogMessage) -> None:
    import json
    print(json.dumps({"level": effect.level.name, "message": str(effect.message)}))

with fx.handler(json_handler, LogMessage):
    log_info("This outputs as JSON")
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Type checking
pyright

# Linting
ruff check src/ tests/
ruff format src/ tests/
```

## License

MIT
