# Repo2Text

A lightweight Python tool that converts repository code into AI-friendly text format. Perfect for providing code context to ChatGPT, Claude, or other AI assistants.

Available as both a **CLI** (`rtt`) and a **GUI** (`main.py`).

## Features

- 📁 **Directory Scanning** - Recursively scan project directories
- 🎯 **Selective Merging** - Filter by file extensions
- 🤖 **AI-Optimized Output** - Formatted with relative file paths and content
- 🌳 **File Tree** - Visual tree of project structure included in output
- 📋 **Clipboard Support** - Copy output directly to clipboard
- 🔧 **Extension Filtering** - Support for `.py`, `.js`, `.swift`, `.java`, and more

## Installation

```bash
git clone https://github.com/essamsoft/Repo2Text-GUI.git
cd Repo2Text-GUI
pip install -e .
```

This installs the `rtt` command globally.

## CLI Usage

```bash
rtt <path>                        # All files in directory
rtt <path> .py .swift             # Only specific extensions
rtt <path> .py -o output.txt      # Export to file
rtt <path> .py -c                 # Copy to clipboard
rtt <path> --tree                 # Show file tree only
```

### Examples

```bash
# Merge all Python files from a project
rtt ~/Projects/my-app .py

# Merge Swift and Objective-C files, copy to clipboard
rtt ~/Projects/ios-app .swift .m .h -c

# Preview project structure without content
rtt ~/Projects/web-app .ts .tsx --tree

# Save merged output to a file
rtt ~/Projects/backend .py .sql -o context.txt
```

## GUI Usage

```bash
python main.py
```

1. Select your project directory
2. Choose file extensions to scan
3. Check the files you want to include
4. Click "Generate & Merge Code" to copy formatted output

## Requirements

- Python 3.6+
- tkinter (included with most Python installations, only needed for GUI)

## Example Output

```text
my-app/
├── src/
│   ├── main.py
│   └── utils.py
└── tests/
    └── test_main.py

========================================

// src/main.py

def main():
    print("hello")

----------------------------------------

// src/utils.py

def helper():
    pass
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Feel free to open issues or submit pull requests.
