# CAPES Research Wizard

A desktop application for searching and extracting article metadata from the CAPES Periodicals Portal.

## Features

- Search the CAPES Periodicals Portal using multiple search queries
- Configure search parameters including advanced search syntax
- View and filter search results
- Export article metadata to CSV with configurable fields
- Parallel processing for faster searches

## Installation

### Windows

Download the latest installer from the [Releases](https://github.com/username/capes-wizard/releases) page and run it.

### From Source

```bash
# Clone the repository
git clone https://github.com/username/capes-wizard.git
cd capes-wizard

# Install with uv
uv venv
uv pip install -e .

# Run the application
python -m wizard.main
```

## Usage

1. **Add Search Queries**
   - Click "Add Query" to add a new search query
   - Enter a theme and search terms
   - Toggle advanced search syntax for complex queries

2. **Configure Settings**
   - Adjust concurrent workers for parallel processing
   - Set request delay to avoid overloading the server
   - Limit the number of pages to scrape per search

3. **Run Searches**
   - Click the play button next to each query to start searching
   - Monitor progress in the status bar
   - View results in the bottom table

4. **Export Results**
   - Click "Export Papers" to save results to a CSV file
   - Select which fields to include in the export
   - Choose a location for the exported file

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv pip install -e .[dev,test]

# Run tests
pytest

# Run linting
flake8 src tests
```

### Project Structure

```
wizard/
├── src/               # Source code
│   └── wizard/        
│       ├── core/      # Core functionality (scraper, parser, exporter)
│       ├── ui/        # User interface components
│       └── utils/     # Utilities (logging, configuration)
├── tests/             # Test suite
└── resources/         # Resources (icons, etc.)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
