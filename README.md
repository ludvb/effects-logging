# effects-logging

Python logging and progress bar library built on the [effects](https://github.com/ludvb/effects) library.

## Installation

```bash
pip install git+https://github.com/ludvb/effects-logging.git
```

## Usage

```python
import sys
import time
import effects as fx
from effects_logging import log_info, log_warning, progressbar, text_writer

def process_items(items):
    log_info(f"Starting processing for {len(items)} items.")
    processed_count = 0
    
    # Use progressbar to wrap the iterable
    for i in progressbar(items, initial_desc="Processing"):
        # Simulate some work
        time.sleep(0.1)
        if i % 3 == 0:
            log_warning(f"Item {i} caused a warning.")
        processed_count += 1
        
    log_info(f"Finished processing {processed_count} items.")

# Define the items to process
my_items = range(10)

# Use text_writer to handle logging and progress bars
with text_writer(sys.stdout):
    process_items(my_items)
```

When run, this will output formatted log messages and a progress bar to your terminal.

### Writing to Files

You can direct output to files, and the library automatically detects whether the output is a TTY (terminal) or file:

```python
from effects_logging import log_info, log_error, progressbar, text_writer

# Write to a file - progress bars are disabled for file output
with open("app.log", "w") as log_file:
    with text_writer(log_file):
        log_info("Application started")
        for i in progressbar(range(5), initial_desc="Processing"):
            log_info(f"Processed item {i}")
        log_error("An error occurred during processing")

# Write to both stdout and a file
import sys
import effects as fx

with open("app.log", "w") as log_file:
    with fx.stack(
        text_writer(sys.stdout),  # TTY output with progress bars
        text_writer(log_file),    # File output without progress bars
    ):
        log_info("This goes to both stdout and file")
        for i in progressbar(range(3), initial_desc="Working"):
            log_info(f"Step {i}")
```

### Progress Bar Description Callback

Update the progress bar description dynamically based on the current item:

```python
import sys
import time
import effects as fx
from effects_logging import progressbar, text_writer

def process_file(filename):
    # Simulate work based on file type
    time.sleep(0.5 if filename.endswith(".pdf") else 0.2)

def process_all_files():
    files = ["file_a.txt", "report.pdf", "image.jpg"]
    
    for f in progressbar(files, desc_callback=lambda item: f"Processing {item}"):
        process_file(f)

# Use text_writer to handle progress bars
with text_writer(sys.stdout):
    process_all_files()
```

### Nested Progress Bars

You can nest progress bars for complex processing workflows:

```python
import sys
import time
import effects as fx
from effects_logging import log_info, progressbar, text_writer

def process_batch(batch_id, items):
    log_info(f"Starting batch {batch_id}")
    
    for item in progressbar(items, desc_callback=lambda x: f"Batch {batch_id}: Item {x}"):
        # Simulate sub-processing
        for sub_item in progressbar(range(3), initial_desc=f"Sub-processing {item}"):
            time.sleep(0.1)
    
    log_info(f"Completed batch {batch_id}")

# Process multiple batches
batches = [
    (1, [1, 2, 3]),
    (2, [4, 5, 6, 7]),
    (3, [8, 9])
]

with text_writer(sys.stdout):
    for batch_id, items in progressbar(batches, initial_desc="Processing batches"):
        process_batch(batch_id, items)
```

### Available Log Levels

```python
import sys
import effects as fx
from effects_logging import log_debug, log_info, log_warning, log_error, LogLevel, text_writer

with text_writer(sys.stdout):
    log_debug("Debug message")      # LogLevel.DEBUG (0)
    log_info("Info message")        # LogLevel.INFO (10)  
    log_warning("Warning message")  # LogLevel.WARNING (50)
    log_error("Error message")      # LogLevel.ERROR (100)
```

### Graceful Degradation

The library gracefully handles cases where no `text_writer` is active:

```python
from effects_logging import log_info, progressbar

# Without text_writer, logs show as warnings and progressbar passes through
log_info("This will show as a warning")

# Progress bars still work, just without visual progress indication
for item in progressbar([1, 2, 3], initial_desc="Processing"):
    print(f"Processing {item}")  # This will still print normally
```

### Asynchronous Progress Bars

Progress bars can be updated in a background thread by passing `progressbar_async=True` to `text_writer`:

```python
with text_writer(sys.stdout, progressbar_async=True):
    # ...
```

## Contributing

Contributions are welcome! Please feel free to open an issue to report bugs or suggest features, or submit a pull request with improvements.

## License

This project is licensed under the MIT License.
