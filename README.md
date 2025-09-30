# Nifty 50 Data Pipeline

A robust data pipeline for fetching and storing NIFTY 50 tick and OHLC data using Shoonya API and PostgreSQL.

## Features

- Fetch real-time tick data for NIFTY 50
- Collect 1-minute OHLC (Open, High, Low, Close) data
- Efficient PostgreSQL storage with optimized schema
- Automated data pipeline with error handling and retries
- Comprehensive logging and monitoring
- Utility functions for data analysis

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure PostgreSQL:
   - Install PostgreSQL
   - Create database and user
   - Update config/config.yaml with credentials

5. Set up environment variables:
   - Copy `secrets.env.example` to `secrets.env`
   - Add your Shoonya API credentials

## Project Structure

```
nifty/
├── src/
│   ├── api/          # Shoonya API integration
│   ├── db/           # Database operations
│   ├── pipeline/     # Data pipeline logic
│   └── utils/        # Helper functions
├── config/           # Configuration files
├── tests/            # Unit tests
├── logs/             # Log files
└── requirements.txt  # Python dependencies
```

## Usage

1. Start the data pipeline:
   ```bash
   python src/pipeline/main.py
   ```

2. Monitor logs:
   ```bash
   tail -f logs/nifty_pipeline.log
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License