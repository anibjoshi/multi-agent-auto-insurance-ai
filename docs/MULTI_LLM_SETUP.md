# Multi-LLM Provider Support

The multi-agent auto insurance claim processing system now supports multiple LLM providers, giving you flexibility to choose the best model for your needs.

## Supported Providers

| Provider | Models | Speed | Cost | Best For |
|----------|--------|-------|------|----------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | Medium | High | Highest quality reasoning |
| **Anthropic** | Claude-3.5-Sonnet, Claude-3-Opus | Medium | High | Long context, safety |
| **Google** | Gemini-1.5-Pro, Gemini-1.5-Flash | Fast | Medium | Fast processing, multimodal |
| **Groq** | Llama-3.1-70B, Mixtral-8x7B | Very Fast | Low | Speed, cost-effective |

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Choose your provider
LLM_PROVIDER=openai

# Add your API keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### 3. Test Providers

Use the setup script to test providers:
```bash
python scripts/setup_providers.py
```

## Usage Examples

### Command Line Testing

Test with specific provider:
```bash
# Test with OpenAI
python benchmarks/scripts/quick_test.py --provider openai --claims 5

# Test with Claude
python benchmarks/scripts/quick_test.py --provider anthropic --claims 3

# Test with Gemini
python benchmarks/scripts/quick_test.py --provider google --claims 5

# Test with Llama via Groq
python benchmarks/scripts/quick_test.py --provider groq --claims 5
```

### API Usage

Start the API server:
```bash
python api/main.py
```

Process claims with different providers:
```bash
# Use default provider
curl -X POST "http://localhost:8000/process-claim" \
  -H "Content-Type: application/json" \
  -d @sample_claim.json

# Use specific provider
curl -X POST "http://localhost:8000/process-claim?provider=anthropic" \
  -H "Content-Type: application/json" \
  -d @sample_claim.json

# Switch default provider
curl -X POST "http://localhost:8000/switch-provider" \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq"}'
```

### Python Code Usage

```python
from src.workflow import ClaimProcessingWorkflow
from src.models import ClaimData

# Initialize with specific provider
workflow = ClaimProcessingWorkflow(provider="anthropic")

# Or use environment variable
workflow = ClaimProcessingWorkflow()  # Uses LLM_PROVIDER from .env

# Process claim
result = await workflow.process_claim(claim_data)
```

## API Key Setup

### OpenAI
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new secret key
3. Set `OPENAI_API_KEY=sk-...`

### Anthropic (Claude)
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Set `ANTHROPIC_API_KEY=sk-ant-...`

### Google (Gemini)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Set `GOOGLE_API_KEY=AI...`

### Groq (Llama)
1. Visit [Groq Console](https://console.groq.com/keys)
2. Create API key
3. Set `GROQ_API_KEY=gsk_...`

## Configuration Options

### Model Selection

Each provider supports multiple models:

```bash
# OpenAI models
OPENAI_MODEL=gpt-4-turbo-preview  # Most capable
OPENAI_MODEL=gpt-4                # Stable
OPENAI_MODEL=gpt-3.5-turbo        # Fastest/cheapest

# Anthropic models
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Latest, best
ANTHROPIC_MODEL=claude-3-opus-20240229      # Most capable
ANTHROPIC_MODEL=claude-3-haiku-20240307     # Fastest

# Google models
GOOGLE_MODEL=gemini-1.5-pro    # Most capable
GOOGLE_MODEL=gemini-1.5-flash  # Fastest
GOOGLE_MODEL=gemini-1.0-pro    # Stable

# Groq models
GROQ_MODEL=llama-3.1-70b-versatile  # Most capable
GROQ_MODEL=llama-3.1-8b-instant     # Fastest
GROQ_MODEL=mixtral-8x7b-32768       # Good balance
```

### Model Parameters

```bash
TEMPERATURE=0.1    # Low for consistent decisions
MAX_TOKENS=1000    # Limit response length
```

## Performance Considerations

### Speed
- **Groq**: Fastest (100-500ms per agent)
- **Google**: Fast (200-800ms per agent)
- **OpenAI/Anthropic**: Medium (500-2000ms per agent)

### Cost (per 1K tokens)
- **Groq**: ~$0.001 (cheapest)
- **Google**: ~$0.005
- **Anthropic**: ~$0.015
- **OpenAI**: ~$0.030 (most expensive)

### Quality
- **OpenAI GPT-4**: Highest reasoning quality
- **Anthropic Claude**: Best for complex logic
- **Google Gemini**: Good balance
- **Groq Llama**: Good for simple tasks

## Rate Limiting

The system automatically adjusts rate limiting based on provider:

- **Groq**: 100ms delay between agents (fastest)
- **Google**: 200ms delay
- **Anthropic**: 300ms delay
- **OpenAI**: 500ms delay (most conservative)

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ❌ OPENAI_API_KEY not found!
   ```
   Solution: Set the appropriate environment variable

2. **Provider Not Supported**
   ```
   ❌ Unsupported provider: xyz
   ```
   Solution: Use one of: openai, anthropic, google, groq

3. **Import Error**
   ```
   ImportError: langchain-anthropic is required
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

### Testing Setup

Use the interactive setup script:
```bash
python scripts/setup_providers.py
```

This will:
- Show provider information
- Check API key status
- Test individual providers
- Create environment templates

## Best Practices

1. **Development**: Use Groq for fast iteration
2. **Production**: Use OpenAI or Anthropic for highest quality
3. **Cost-sensitive**: Use Google Gemini or Groq
4. **High-volume**: Use Google or Groq for better rate limits

## Model Recommendations

### By Use Case

- **Highest Accuracy**: OpenAI GPT-4 or Anthropic Claude-3.5-Sonnet
- **Best Speed**: Groq Llama-3.1-8B or Google Gemini-1.5-Flash
- **Best Value**: Groq Llama-3.1-70B or Google Gemini-1.5-Pro
- **Complex Reasoning**: Anthropic Claude-3-Opus or OpenAI GPT-4

### System Resources

The multi-agent system processes 9 agents sequentially, so total time = agent_time × 9:

- **Groq**: ~1-5 seconds total
- **Google**: ~2-8 seconds total  
- **Anthropic/OpenAI**: ~5-20 seconds total

Choose based on your latency requirements and budget constraints. 