# Nifty 50 Data Pipeline

A robust data pipeline for fetching and storing NIFTY 50 tick and OHLC data using Shoonya API and PostgreSQL.

## Features

- Fetch real-time tick data for NIFTY 50
- Collect 1-minute OHLC (Open, High, Low, Close) data
- Efficient PostgreSQL storage with optimized schema
- Automated data pipeline with error handling and retries
- Comprehensive logging and monitoring
- Utility functions for data analysis

## Project Structure

```
nifty/
├── src/
│   ├── api/          # Shoonya API integration
│   ├── db/           # Database operations
│   ├── pipeline/     # Data pipeline logic
│   └── utils/        # Helper functions
├── config/           # (Optional) Additional configs
├── tests/            # Unit tests
├── logs/             # Log files
└── requirements.txt  # Python dependencies
```
## License

MIT License