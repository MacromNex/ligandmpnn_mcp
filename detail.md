# LigandMPNN MCP

> AI-powered protein design toolkit for scaffold-based sequence generation and ligand-aware protein design using LigandMPNN through Model Context Protocol (MCP)

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The LigandMPNN MCP provides comprehensive protein design capabilities through both direct script execution and MCP integration. This toolkit enables scaffold-based protein sequence generation with support for ligand-aware design, constrained optimization, and sequence likelihood calculation.

### Features
- **Protein-Ligand Complex Design**: Context-aware sequence generation considering ligand binding
- **Constrained Design**: Fixed/redesigned residue specification with flexible constraints
- **Sequence Scoring**: Likelihood calculation and probability estimation for protein sequences
- **Batch Processing**: Submit large-scale design jobs for background processing
- **Side Chain Packing**: Combined sequence design and structural optimization
- **Multiple Model Support**: ProteinMPNN, LigandMPNN, and SolubleMPNN variants

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   ├── server.py           # MCP server
│   └── jobs/               # Job management system
├── scripts/
│   ├── protein_design.py   # Basic protein sequence design
│   ├── ligand_design.py    # Ligand-aware protein design
│   ├── sequence_scoring.py # Sequence likelihood calculation
│   ├── constrained_design.py # Constrained design with fixed residues
│   └── lib/                # Shared utilities
├── examples/
│   └── data/               # Demo PDB structures and configs
├── configs/                # Configuration files
└── repo/                   # Original LigandMPNN repository
```

---

## Installation

### Quick Setup (Recommended)

Run the automated setup script:

```bash
cd ligandmpnn_mcp
bash quick_setup.sh
```

The script will create the conda environment, clone the LigandMPNN repository, install all dependencies, and display the Claude Code configuration. See `quick_setup.sh --help` for options like `--skip-env` or `--skip-repo`.

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- CUDA-capable GPU (optional, but recommended for performance)

### Manual Installation (Alternative)

If you prefer manual installation or need to customize the setup, follow `reports/step3_environment.md`:

```bash
# Navigate to the MCP directory
cd /path/to/ligandmpnn_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.11 -y

# Activate environment
mamba activate ./env

# Install Dependencies
pip install -r repo/LigandMPNN/requirements.txt

# Install MCP dependencies
pip install fastmcp loguru --ignore-installed
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/protein_design.py` | Basic protein sequence design using ProteinMPNN | See below |
| `scripts/ligand_design.py` | Ligand-aware protein design using LigandMPNN | See below |
| `scripts/sequence_scoring.py` | Protein sequence likelihood calculation | See below |
| `scripts/constrained_design.py` | Constrained design with fixed/redesigned residues | See below |

### Script Examples

#### Basic Protein Design

```bash
# Activate environment
mamba activate ./env

# Run protein design
python scripts/protein_design.py \
  --input examples/data/1BC8.pdb \
  --output results/protein_design \
  --num_sequences 3 \
  --temperature 0.1
```

**Parameters:**
- `--input, -i`: Input PDB file (required)
- `--output, -o`: Output directory (default: results/)
- `--num_sequences, -n`: Number of sequences to generate (default: 3)
- `--temperature, -t`: Sampling temperature for diversity (default: 0.1)
- `--config, -c`: Configuration file (optional)

#### Ligand-Aware Design

```bash
python scripts/ligand_design.py \
  --input examples/data/1BC8.pdb \
  --output results/ligand_design \
  --num_sequences 3 \
  --use_atom_context
```

**Parameters:**
- `--use_atom_context`: Enable ligand atom context (recommended)
- `--use_side_chain_context`: Enable side chain context
- `--no_ligand_context`: Disable ligand context

#### Sequence Scoring

```bash
python scripts/sequence_scoring.py \
  --input examples/data/1BC8.pdb \
  --sequences "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" \
  --output results/scoring.pt
```

**Parameters:**
- `--sequences`: Protein sequences to score (comma or slash separated)
- `--sequences_file`: FASTA file with sequences to score
- `--save_probs`: Save per-residue probabilities

#### Constrained Design

```bash
python scripts/constrained_design.py \
  --input examples/data/1BC8.pdb \
  --output results/constrained \
  --fixed_residues "C1 C2 C3" \
  --num_sequences 2
```

**Parameters:**
- `--fixed_residues`: Residues to keep unchanged (space/comma separated)
- `--redesigned_residues`: Specific residues to redesign
- `--chains_to_design`: Specific chains to design

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name LigandMPNN
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add LigandMPNN -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "LigandMPNN": {
      "command": "/path/to/ligandmpnn_mcp/env/bin/python",
      "args": ["/path/to/ligandmpnn_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from LigandMPNN?
```

#### Basic Protein Design
```
Use simple_design with input file @examples/data/1BC8.pdb and generate 5 sequences
```

#### Ligand-Aware Design
```
Run ligand_design on @examples/data/1BC8.pdb with ligand context enabled
```

#### Sequence Scoring
```
Score this sequence using @examples/data/1BC8.pdb as reference: "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
```

#### Constrained Design
```
Use constrained_design with @examples/data/1BC8.pdb, fixing residues 1, 2, and 3
```

#### Long-Running Tasks (Submit API)
```
Submit large design job for @examples/data/1BC8.pdb with 100 sequences
Then check the job status
```

#### Batch Processing
```
Process these files in batch:
- @examples/data/1BC8.pdb
- @examples/data/2GFB.pdb
- @examples/data/4GYT.pdb
```

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "LigandMPNN": {
      "command": "/path/to/ligandmpnn_mcp/env/bin/python",
      "args": ["/path/to/ligandmpnn_mcp/src/server.py"]
    }
  }
}
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `simple_design` | Basic protein sequence design | `input_file`, `chains`, `num_sequences`, `temperature` |
| `sequence_scoring` | Score protein sequences | `input_file`, `fasta_sequences`, `save_probs` |
| `constrained_design` | Design with fixed/redesigned positions | `input_file`, `chains_to_design`, `fixed_positions`, `num_sequences` |
| `ca_only_design` | Design using only carbon alpha atoms | `input_file`, `chains`, `model`, `num_sequences` |
| `validate_pdb_structure` | Validate PDB file compatibility | `input_file` |
| `list_example_structures` | List available example structures | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_batch_design` | Batch processing multiple files | `input_dir`, `file_pattern`, `chains`, `num_sequences` |
| `submit_large_design` | Large-scale sequence generation | `input_file`, `chains`, `num_sequences`, `temperature` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs |

---

## Examples

### Example 1: Basic Protein Design

**Goal:** Generate diverse sequences for 1BC8 (93-residue protein with ligand)

**Using Script:**
```bash
python scripts/protein_design.py \
  --input examples/data/1BC8.pdb \
  --output results/basic_design \
  --num_sequences 5 \
  --temperature 0.1
```

**Using MCP (in Claude Code):**
```
Use simple_design with input_file @examples/data/1BC8.pdb and num_sequences 5 to generate diverse protein sequences
```

**Expected Output:**
- 5 FASTA sequence files in `results/basic_design/seqs/`
- Generated sequences for 93 residues in chain A
- Execution time: ~15 seconds
- Design statistics showing sequence diversity

### Example 2: Ligand-Aware Design

**Goal:** Design protein sequences optimized for ligand binding

**Using Script:**
```bash
python scripts/ligand_design.py \
  --input examples/data/1BC8.pdb \
  --output results/ligand_aware/ \
  --num_sequences 3 \
  --use_atom_context
```

**Using MCP (in Claude Code):**
```
Run ligand_design on @examples/data/1BC8.pdb with atom context enabled and generate 3 sequences
```

**Expected Output:**
- Ligand-aware designed sequences
- Optimized protein-ligand binding interfaces
- Confidence scores for ligand interactions

### Example 3: Sequence Likelihood Scoring

**Goal:** Score the native sequence of 1BC8 to validate model performance

**Using MCP (in Claude Code):**
```
Use sequence_scoring with @examples/data/1BC8.pdb to score this native sequence: "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
```

**Expected Output:**
- `results/1BC8.pt` file (271KB PyTorch tensor)
- Likelihood scores for the 93-residue sequence
- Execution time: ~3 seconds
- High scores indicating native sequence compatibility

### Example 4: Constrained Design

**Goal:** Design 1BC8 while keeping N-terminal residues fixed

**Using MCP (in Claude Code):**
```
Use constrained_design with @examples/data/1BC8.pdb and fixed_positions "1 2 3" to preserve N-terminal while redesigning the rest
```

**Expected Output:**
- Fixed residues: ['C1', 'C2', 'C3'] (positions 1-3)
- Redesigned residues: ['C4', 'C5', ..., 'C93'] (positions 4-93)
- Execution time: ~4 seconds
- Constraint satisfaction verified in output

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `1BC8.pdb` | Small protein-ligand complex (142KB, 93 residues) | All design tools |
| `2GFB.pdb` | Large protein structure with insertion codes (2.3MB) | Stress testing, batch |
| `4GYT.pdb` | Multi-chain protein complex (525KB) | Multi-chain design |
| `bias_AA_per_residue.json` | Per-residue amino acid bias configuration | Constrained design |
| `omit_AA_per_residue.json` | Per-residue amino acid omission rules | Constrained design |
| `pdb_ids.json` | Multi-structure processing configuration | Batch processing |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `default_config.json` | Comprehensive default settings | 45 parameters |
| `protein_design_config.json` | Basic protein design settings | Model type, temperature, processing |
| `ligand_design_config.json` | Ligand-aware design settings | Ligand context, side chains |
| `sequence_scoring_config.json` | Sequence scoring settings | Model type, probability saving |
| `constrained_design_config.json` | Constrained design settings | Fixed residues, constraints |

### Config Example

```json
{
  "_description": "Basic protein design configuration",
  "model": {
    "model_type": "protein_mpnn",
    "temperature": 0.1,
    "seed": 111
  },
  "processing": {
    "batch_size": 1,
    "verbose": 1
  },
  "constraints": {
    "fixed_residues": "",
    "redesigned_residues": ""
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.10 -y
mamba activate ./env
pip install -r requirements.txt
```

**Problem:** Import errors
```bash
# Verify installation
python -c "from src.server import mcp"
```

**Problem:** CUDA/PyTorch issues
```bash
# Check CUDA availability
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Reinstall PyTorch if needed
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove LigandMPNN
claude mcp add LigandMPNN -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
cat jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

---

## Performance Characteristics

| Operation Type | Typical Runtime | Memory Usage | Concurrency |
|---------------|-----------------|--------------|-------------|
| Single design (1-10 seqs) | 5-15 seconds | ~1GB | Up to 4 concurrent |
| Batch design (10+ files) | 10-60 minutes | ~1-2GB | 1 at a time |
| Sequence scoring | 3-8 seconds | ~0.5GB | Up to 8 concurrent |
| Validation | <1 second | ~10MB | Unlimited |

---

## License

This project is based on [LigandMPNN](https://github.com/dauparas/LigandMPNN) and maintains the same MIT license.

## Credits

Based on [LigandMPNN](https://github.com/dauparas/LigandMPNN) by Dauparas et al.
- Original Paper: [Robust deep learning–based protein sequence design using ProteinMPNN](https://www.science.org/doi/10.1126/science.add2187)
- LigandMPNN Paper: [Atomic context-conditioned protein sequence design using LigandMPNN](https://www.biorxiv.org/content/10.1101/2023.12.13.571462v1)
