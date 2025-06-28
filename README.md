# ReAct Multi-Agent Auto Insurance Claim Processing System

A production-grade ReAct multi-agent AI system for automated auto insurance claim processing using LangGraph, tool calling, and OpenAI GPT models.

## 🎯 Overview

This system implements a sophisticated **ReAct (Reasoning + Acting) multi-agent workflow** that processes auto insurance claims through 10 specialized AI agents. Each agent uses the ReAct pattern with tool calling to reason about claims and access structured data, providing transparent decision-making with detailed reasoning trails. The system uses LangGraph for orchestration and provides both programmatic and REST API interfaces.

## ✨ Features

- **🤖 10 Specialized ReAct Agents**: Each agent uses reasoning + acting pattern with domain-specific tools
- **🔧 Tool-Based Data Access**: Structured tools replace raw JSON prompts for reliable data access
- **🧠 Advanced Reasoning**: Step-by-step reasoning trails with tool usage documentation
- **⚡ Parallel Processing**: ReAct agents run concurrently for fast claim processing
- **🔄 LangGraph Orchestration**: Production-grade workflow management with state isolation
- **🌐 REST API**: FastAPI-based web service with interactive documentation
- **📊 Detailed Audit Trails**: Complete reasoning and tool usage history for each decision
- **🚀 Batch Processing**: Handle multiple claims efficiently with proper data isolation
- **📈 Production Ready**: Comprehensive error handling, logging, and monitoring

## 🏗️ ReAct System Architecture

The system uses a **ReAct (Reasoning + Acting) pattern** with tool calling for sophisticated claim analysis:

### ReAct Pattern Benefits
- **🧠 Reasoning**: Agents think step-by-step about claim requirements
- **🔧 Acting**: Agents use specialized tools to gather and analyze data
- **📊 Transparency**: Complete reasoning and tool usage audit trail
- **🎯 Accuracy**: Structured data access reduces hallucination risks

### Stage 1: Parallel ReAct Agent Processing
Nine specialized ReAct agents analyze the claim simultaneously using domain-specific tools:

1. **PolicyValidator** - Validates policy timing and eligibility using policy and date calculation tools
2. **DocumentValidator** - Ensures required documents using claim info and documentation tools
3. **DriverVerifier** - Verifies driver eligibility using driver information and coverage tools
4. **VehicleDamageEvaluator** - Assesses damage using vehicle data and total loss calculation tools
5. **CoverageEvaluator** - Enforces limits using policy, vehicle, coverage, and liability tools
6. **CatastropheChecker** - Handles CAT events using claim and catastrophe information tools
7. **LiabilityAssessor** - Allocates fault using liability and documentation tools
8. **RentalBenefitChecker** - Evaluates rental benefits using rental and coverage tools
9. **FraudDetector** - Detects fraud using vehicle, mileage, CAT, and timing analysis tools

### Stage 2: Final ReAct Decision
10. **ClaimDecider** - Uses ReAct pattern to aggregate all agent responses and make final decisions

### Tool Categories
- **📋 Data Access Tools**: `get_claim_basic_info`, `get_policy_information`, `get_driver_information`, etc.
- **🔍 Analysis Tools**: `check_total_loss_threshold`, `check_mileage_discrepancy`
- **📅 Calculation Tools**: `calculate_days_between_dates`
- **🏷️ Specialized Tools**: `get_catastrophe_information`, `get_liability_information`, etc.

## 🚀 Quick Start

1. **Install the Package**
   ```bash
   # Install with pip
   pip install -e .
   
   # Or use make (recommended for development)
   make install
   ```

2. **Configure Environment**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

3. **Test the System**
   ```bash
   make test
   # Or directly: python tests/test_system.py
   ```

4. **Run ReAct Demo**
   ```bash
   make demo
   # Or directly: python scripts/demo_react.py
   
   # Run the new ReAct-specific demo
   python scripts/demo_react.py
   ```

5. **Process Datasets** (for benchmarking)
   ```bash
   # Convert datasets to scalable JSONL format
   make process-datasets
   ```

6. **Run Accuracy Benchmarks**
   ```bash
   # Quick test (5 claims for development)
   make quick-benchmark
   
   # Full benchmark (customizable)
   make benchmark
   
   # Full benchmark on 450 claims
   make benchmark-full
   ```

7. **Manage Prompts (Optional)**
   ```bash
   # List all available prompts  
   PYTHONPATH=. python scripts/prompt_manager.py list
   
   # View a specific agent's prompt
   PYTHONPATH=. python scripts/prompt_manager.py show --agent PolicyValidator
   
   # Validate all prompts
   PYTHONPATH=. python scripts/prompt_manager.py validate
   ```

8. **Start API Server**
   ```bash
   make api
   # Or directly: python api/main.py
   ```

9. **Access Documentation**
   Visit `http://localhost:8000/docs` for interactive API documentation

## 📖 Usage Example

### Process a Claim via API

```python
import requests

claim_data = {
    "claim_id": "CLM-2025-001",
    "incident_date": "2025-01-20",
    "report_date": "2025-01-22",
    "state": "TX",
    "driver_name": "John Doe",
    "damage_type": "collision",
    "repair_estimate": 5000,
    # ... other required fields
}

response = requests.post(
    "http://localhost:8000/claims/process",
    json={"claim_data": claim_data, "include_agent_details": True}
)

result = response.json()
print(f"Decision: {result['final_decision']['status']}")
print(f"Reason: {result['final_decision']['explanation']}")
```

### Process Claims Programmatically

```python
from src import ClaimProcessingWorkflow, ClaimData

# Initialize workflow
workflow = ClaimProcessingWorkflow(openai_api_key="your_key_here")

# Process claim
claim = ClaimData(**claim_data)
result = await workflow.process_claim(claim)

print(f"Final Decision: {result.final_decision.status}")
for response in result.agent_responses:
    print(f"{response.agent}: {response.status} - {response.explanation}")
```

## 🔧 Configuration

The system supports various configuration options through environment variables:

- **OpenAI Settings**: API key, model selection, temperature
- **API Configuration**: Host, port, CORS settings
- **Logging**: Log levels, output formats
- **Performance**: Batch sizes, timeout settings

See [SETUP.md](SETUP.md) for detailed configuration instructions.

## 📊 Agent Decision Logic

Each agent implements specific business rules:

- **APPROVED**: All criteria met, proceed with claim
- **REJECTED**: Critical failure, deny claim
- **PARTIAL**: Approve with limitations or reduced amount
- **ESCALATE**: Requires human review or additional investigation

The ClaimDecider aggregates responses using priority rules:
1. Any REJECTED → Overall REJECTED
2. Any ESCALATE → Overall ESCALATE  
3. Any PARTIAL → Overall PARTIAL
4. All APPROVED → Overall APPROVED

## 📝 Prompt Management System

The system uses **file-based prompts** co-located with agent code for easy editing and version control.

### Key Benefits
- **🔄 Easy Iteration**: Modify prompts without touching code
- **👥 Team Collaboration**: Non-developers can improve prompts
- **🧹 Clean Architecture**: Prompts live alongside agent implementations

### Prompt Structure
```
src/agents/                      # ReAct prompts + agent code (co-located)
├── policy_validator.py         # Python agent implementation
├── policy_validator.md         # ReAct prompt file
├── fraud_detector.py           # Python agent implementation  
├── fraud_detector.md           # ReAct prompt file
├── claim_decider.py            # Python agent implementation
├── claim_decider.md            # ReAct prompt file
└── ...                         # (co-located .py and .md files)

agents/                         # Legacy reference
├── v1/                        # Original prompts
└── v2/                        # Traditional prompts
```

### Simple Management
```bash
# List all prompts
PYTHONPATH=. python scripts/prompt_manager.py list

# View specific prompt
PYTHONPATH=. python scripts/prompt_manager.py show --agent PolicyValidator

# Validate prompts
PYTHONPATH=. python scripts/prompt_manager.py validate
```

### ReAct Prompt Format
Each prompt includes:
- **Role Definition**: Clear agent responsibilities
- **Available Tools**: Domain-specific tool descriptions  
- **Business Rules**: Systematic decision criteria
- **ReAct Process**: Step-by-step reasoning framework
- **Output Format**: Consistent JSON response structure

## 🛡️ Production Considerations

- **Security**: API key management, HTTPS, authentication
- **Scaling**: Rate limiting, request queuing, load balancing
- **Monitoring**: Logging, metrics, health checks
- **Compliance**: Data privacy, audit trails, regulatory requirements

## 📁 Project Structure

```
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Data models and schemas
│   ├── workflow.py              # LangGraph workflow orchestration
│   ├── config.py                # Configuration management
│   ├── tools.py                 # ReAct agent tools
│   ├── prompt_loader.py         # Prompt file management
│   ├── py.typed                 # Type checking marker
│   └── agents/                  # Agent implementations and prompts
│       ├── __init__.py
│       ├── base.py              # Base agent classes
│       ├── policy_validator.py  # Agent implementation
│       ├── policy_validator.md  # ReAct prompt file
│       ├── fraud_detector.py    # Agent implementation
│       ├── fraud_detector.md    # ReAct prompt file
│       └── ...                  # (all agents with co-located .py and .md files)
├── api/                          # REST API
│   ├── __init__.py
│   └── main.py                  # FastAPI application
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_system.py           # Comprehensive tests
│   └── test_react_agents.py     # ReAct agent unit tests
├── scripts/                      # Utility scripts
│   ├── __init__.py
│   ├── demo_react.py            # ReAct agent demonstration
│   └── prompt_manager.py        # Prompt management utility
├── docs/                         # Documentation
│   └── SETUP.md                 # Setup instructions
├── agents/                       # Legacy prompt definitions
│   ├── v1/                      # Version 1 prompts
│   └── v2/                      # Version 2 prompts
├── dataset/                      # Sample data
│   ├── auto_claim_sample_inputs.json
│   └── ...
├── requirements.txt              # Dependencies
├── setup.py                      # Package setup (legacy)
├── pyproject.toml               # Modern package configuration
├── Makefile                     # Development commands
└── README.md                    # This file
```

## 🤝 Contributing

This is a baseline implementation demonstrating multi-agent claim processing. Areas for enhancement:

- **Advanced Reasoning**: Integration with specialized insurance databases
- **Machine Learning**: Pattern recognition for fraud detection
- **Integration**: Connect with existing insurance systems
- **UI/UX**: Web interface for claim adjusters
- **Analytics**: Business intelligence and reporting features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Getting Started

Ready to process your first claim? Check out [SETUP.md](SETUP.md) for detailed instructions or run the test script to see the system in action!
