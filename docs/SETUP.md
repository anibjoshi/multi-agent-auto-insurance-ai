# Multi-Agent Auto Insurance Claim Processing System - Setup Guide

## Quick Start

### 1. Install the Package

```bash
# Install in development mode (recommended)
pip install -e .

# Or install with make (includes development dependencies)
make install-dev

# For production use
pip install .
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Application Configuration
DEBUG=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
```

**Important:** Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 3. Test the System

Run the test script to verify everything is working:

```bash
# Using make (recommended)
make test

# Or directly
python tests/test_system.py
```

This will:
- Process sample claims through all agents
- Show detailed agent responses
- Test batch processing
- Test edge cases

### 4. Run the Interactive Demo

```bash
# Using make (recommended)
make demo

# Or directly
PYTHONPATH=. python3 scripts/demo_react.py
```

### 5. Start the API Server

```bash
# Using make (recommended)
make api

# Or directly
python api/main.py
```

The API server will start on `http://localhost:8000`

### 6. Access Interactive Documentation

Visit `http://localhost:8000/docs` for the Swagger UI with interactive API documentation.

## Development Commands

The project includes a Makefile with common development tasks:

```bash
make help          # Show all available commands
make install       # Install package and dependencies
make install-dev   # Install with development dependencies
make test          # Run tests
make demo          # Run interactive demo
make api           # Start API server
make clean         # Clean temporary files
make format        # Format code with black
make lint          # Lint code with flake8
make typecheck     # Type check with mypy
```

## API Usage Examples

### Process a Single Claim

```bash
curl -X POST "http://localhost:8000/claims/process" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_data": {
      "claim_id": "CLM-2025-TEST",
      "incident_date": "2025-01-20",
      "report_date": "2025-01-22",
      "state": "TX",
      "policy_start_date": "2024-06-01",
      "policy_end_date": "2025-06-01",
      "driver_name": "John Doe",
      "driver_license_status": "valid",
      "driver_listed_on_policy": true,
      "damage_type": "collision",
      "repair_estimate": 5000,
      ...
    },
    "include_agent_details": true
  }'
```

### Health Check

```bash
curl http://localhost:8000/health
```

### Get Workflow Visualization

```bash
curl http://localhost:8000/workflow/visualization
```

## System Architecture

The system uses LangGraph to orchestrate 10 specialized agents:

1. **PolicyValidator** - Validates policy timing and eligibility
2. **DocumentValidator** - Checks required documents
3. **DriverVerifier** - Verifies driver eligibility
4. **VehicleDamageEvaluator** - Assesses damage coverage
5. **CoverageEvaluator** - Enforces limits and endorsements
6. **CatastropheChecker** - Handles catastrophic events
7. **LiabilityAssessor** - Allocates fault and liability
8. **RentalBenefitChecker** - Evaluates rental benefits
9. **FraudDetector** - Scans for fraud patterns
10. **ClaimDecider** - Makes final approval/rejection decision

## Configuration Options

### OpenAI Models

Supported models:
- `gpt-4-turbo-preview` (recommended for production)
- `gpt-4`
- `gpt-3.5-turbo` (faster, less accurate)

### API Configuration

- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)

### Logging

- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

## Production Considerations

1. **Security**: 
   - Store API keys securely
   - Use HTTPS in production
   - Implement proper authentication

2. **Scaling**:
   - Consider rate limits for OpenAI API
   - Implement request queuing for high volume
   - Add monitoring and observability

3. **Data Privacy**:
   - Ensure compliance with data protection regulations
   - Implement data encryption
   - Consider data retention policies

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Verify your API key is correct
   - Check if you have sufficient credits
   - Ensure the key has proper permissions

2. **Model Not Found**
   - Check if the specified model is available
   - Try switching to a different model

3. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility

### Getting Help

1. Check the logs for detailed error messages
2. Verify your environment configuration
3. Test with the provided sample data
4. Review the API documentation at `/docs` 