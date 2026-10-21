
# Jarvis — Personal AI Assistant

Jarvis is a modular personal AI assistant being developed in Python.

The initial version runs locally on Windows and will use Ollama
to communicate with a locally hosted language model.

## Current capabilities

- Python application entry point
- Environment-based configuration
- Console and file logging
- Automated configuration tests

## Planned capabilities

- Local AI conversations
- Persistent conversation and approved-fact memory
- Permission-controlled tools for laptop operations
- Voice input and spoken responses
- Desktop interface
- Secure Android integration

## Requirements

- Python 3.14
- Ollama installed and running
- A locally available Ollama model

The initial model is `llama3.2:3b`.

## Project structure

Application code is located in `src/jarvis/`.

- `config/` — application settings
- `core/` — central application logic and logging
- `ai/` — AI provider integrations
- `memory/` — persistent storage
- `tools/` — controlled tool execution
- `voice/` — speech features
- `interface/` — user interfaces
- `tests/` — automated tests

Some planned modules have not been implemented yet.

## Run the application

Activate the virtual environment from the project root:

```bash
source .venv/Scripts/activate
```

Run Jarvis:

```bash
PYTHONPATH=src python -m jarvis.main
```

## Run tests

Run the settings tests:

```bash
PYTHONPATH=src python -m unittest tests.test_settings -v
```

Discover and run all tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Configuration

The application reads these environment variables:

| Variable | Default |
|---|---|
| `JARVIS_APP_NAME` | `Jarvis` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL` | `llama3.2:3b` |
| `JARVIS_LOG_LEVEL` | `INFO` |

The settings loader reads environment variables provided to the process.
It does not currently load a `.env` file.

## Development principles

- Build and test one module at a time.
- Prefer Python's standard library when practical.
- Keep modules focused on one responsibility.
- Validate tool inputs and enforce permissions before execution.
- Keep local services private unless secure remote access is explicitly implemented.
