# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LigandMPNN MCP is a Model Context Protocol server wrapping the [LigandMPNN](https://github.com/dauparas/LigandMPNN) protein design toolkit. It exposes protein sequence design, scoring, and constrained design as MCP tools via FastMCP.

## Setup

```bash
bash quick_setup.sh
```

This creates a conda env at `./env`, clones the LigandMPNN repo to `repo/LigandMPNN/`, installs dependencies, and downloads model weights (~15 checkpoint files to `repo/LigandMPNN/model_params/`).

## Running the Server

```bash
./env/bin/python src/server.py
```

## Running Tests

```bash
./env/bin/python tests/integration_tests.py
```

Results are saved to `reports/integration_test_results.json`.

## Docker

```bash
docker build -t ligandmpnn-mcp .
docker run ligandmpnn-mcp
```

The Dockerfile clones the repo and bakes model weights into the image. GitHub Actions (`.github/workflows/docker.yml`) automatically builds and pushes to GHCR on push to main.

## Architecture

### Request Flow

```
Claude Code → FastMCP server (src/server.py)
  → Script function (scripts/*.py)
    → LigandMPNN repo function (repo/LigandMPNN/run.main or score.main)
      → Output files → Collected results → Returned via MCP
```

### Key Layers

- **`src/server.py`**: FastMCP server. Defines all MCP tools. Sync tools call script functions directly; submit tools delegate to `JobManager` for background execution.

- **`src/jobs/manager.py`**: `JobManager` singleton (`job_manager`) handles async jobs. Jobs run in background threads, with metadata persisted to `jobs/<job_id>/metadata.json`. Status enum: PENDING → RUNNING → COMPLETED/FAILED/CANCELLED.

- **`scripts/*.py`**: Each script wraps a LigandMPNN capability. They share a pattern: validate inputs → merge config (defaults + config file + CLI overrides) → create Args object → call repo function → collect outputs. Each has both a `run_*()` function (for MCP) and `__main__` CLI entry.

- **`scripts/lib/`**: Shared utilities — `repo_interface.py` lazy-loads repo functions via `sys.path.insert()`, `paths.py` centralizes path resolution, `validation.py` validates PDB files and parameters, `io.py` handles config/output parsing.

### Configuration Merge Order

```python
config = {**DEFAULT_CONFIG, **(config_file or {}), **cli_overrides}
```

Config JSON files in `configs/` have sections: `model`, `processing`, `ligand_context`, `packing`, `membrane`, `constraints`, `advanced`.

### Tool Categories

| Category | Tools | Execution |
|----------|-------|-----------|
| Sync (fast) | `simple_design`, `sequence_scoring`, `constrained_design`, `ca_only_design` | Direct call, returns result |
| Submit (long) | `submit_batch_design`, `submit_large_design` | Returns job_id, runs in background |
| Job mgmt | `get_job_status`, `get_job_result`, `get_job_log`, `cancel_job`, `list_jobs` | Query job state |
| Utility | `validate_pdb_structure`, `list_example_structures` | Direct call |

### Important Paths

- Model weights: `repo/LigandMPNN/model_params/*.pt`
- Example PDBs: `examples/data/*.pdb`
- Job outputs: `jobs/<job_id>/`
- Design results: `results/`

### Dependencies

Core: `fastmcp`, `torch` (2.2.1, CUDA 12.1), `numpy`, `scipy`, `biopython`, `ProDy`. Optional: `loguru` (falls back to stdlib `logging`).
