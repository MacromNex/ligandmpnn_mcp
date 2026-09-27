# LigandMPNN MCP Integration Test Prompts

## Tool Discovery Tests

### Prompt 1: List All Tools
**Prompt:** "What MCP tools are available from LigandMPNN? Give me a brief description of each."

**Expected Response:** List of 13 tools with descriptions:
- Job management tools: get_job_status, get_job_result, get_job_log, cancel_job, list_jobs
- Sync tools: simple_design, sequence_scoring, constrained_design, ca_only_design
- Submit API tools: submit_batch_design, submit_large_design
- Utility tools: validate_pdb_structure, list_example_structures

### Prompt 2: Tool Details
**Prompt:** "Explain how to use the simple_design tool, including all parameters."

**Expected Response:** Detailed explanation of simple_design parameters

## Sync Tool Tests

### Prompt 3: List Examples
**Prompt:** "Use the list_example_structures tool to show me what example PDB files are available for testing."

**Expected Response:**
```json
{
  "status": "success",
  "examples_dir": "/path/to/examples/data",
  "structures": [...],
  "total_structures": N
}
```

### Prompt 4: Validate PDB File
**Prompt:** "Use validate_pdb_structure to check the file examples/data/1BC8.pdb"

**Expected Response:**
```json
{
  "status": "success",
  "valid": true,
  "chains": [...],
  "num_residues": N,
  "has_ligands": boolean
}
```

### Prompt 5: Simple Protein Design
**Prompt:** "Use simple_design with input_file='examples/data/1BC8.pdb', chains='A', num_sequences=2, temperature=0.1"

**Expected Response:**
```json
{
  "status": "success",
  "generated_sequences": [...],
  "num_sequences": 2,
  "chains": "A"
}
```

### Prompt 6: Error Handling Test
**Prompt:** "Try running validate_pdb_structure with input_file='/nonexistent/file.pdb'"

**Expected Response:**
```json
{
  "status": "error",
  "error": "File not found: /nonexistent/file.pdb",
  "valid": false
}
```

### Prompt 7: Sequence Scoring
**Prompt:** "Use sequence_scoring on examples/data/1BC8.pdb with default parameters"

**Expected Response:**
```json
{
  "status": "success",
  "scores": [...],
  "analysis": {...}
}
```

### Prompt 8: Constrained Design
**Prompt:** "Run constrained_design on examples/data/1BC8.pdb with chains_to_design='A' and fixed_positions='1 2 3'"

**Expected Response:**
```json
{
  "status": "success",
  "constrained_sequences": [...],
  "fixed_positions": ["1", "2", "3"]
}
```

## Submit API Tests

### Prompt 9: Submit Large Design Job
**Prompt:** "Submit a large design job using submit_large_design with input_file='examples/data/1BC8.pdb', chains='A', num_sequences=20"

**Expected Response:**
```json
{
  "status": "submitted",
  "job_id": "job_abc123",
  "message": "Job submitted for processing"
}
```

### Prompt 10: Check Job Status
**Prompt:** "Check the status of job [job_id_from_previous_test]"

**Expected Response:**
```json
{
  "job_id": "job_abc123",
  "status": "pending|running|completed|failed",
  "submitted_at": "timestamp",
  "progress": "..."
}
```

### Prompt 11: List All Jobs
**Prompt:** "Use list_jobs to show all submitted jobs"

**Expected Response:**
```json
{
  "status": "success",
  "jobs": [...],
  "total_jobs": N
}
```

### Prompt 12: Get Job Log
**Prompt:** "Show me the last 10 lines of logs for job [job_id] using get_job_log"

**Expected Response:**
```json
{
  "status": "success",
  "job_id": "job_abc123",
  "log_lines": [...],
  "total_lines": N
}
```

## Batch Processing Tests

### Prompt 13: Batch Design Submit
**Prompt:** "Use submit_batch_design to process all PDB files in examples/data/ with num_sequences=1"

**Expected Response:**
```json
{
  "status": "submitted",
  "job_id": "batch_job_xyz789",
  "files_to_process": [...],
  "total_files": N
}
```

### Prompt 14: Batch Status Check
**Prompt:** "Check the status of the batch job [batch_job_id]"

**Expected Response:**
```json
{
  "job_id": "batch_job_xyz789",
  "status": "running|completed",
  "progress": "X/N files completed"
}
```

## End-to-End Scenarios

### Prompt 15: Full Analysis Workflow
**Prompt:** "Please help me analyze the protein in examples/data/1BC8.pdb:
1. First validate the structure
2. Then run simple sequence design for chain A with 3 sequences
3. Finally score the original sequence"

**Expected:** Sequential execution of multiple tools with results for each step

### Prompt 16: Large Scale Processing
**Prompt:** "I want to do large-scale design. Submit a job to generate 50 sequences for examples/data/1BC8.pdb chain A, then check its progress"

**Expected:** Job submission followed by status check

### Prompt 17: Error Recovery Scenario
**Prompt:** "Try to submit a design job for a non-existent file '/fake/protein.pdb', then show me what error handling looks like"

**Expected:** Proper error message with helpful information

## Parameter Validation Tests

### Prompt 18: Test Invalid Parameters
**Prompt:** "Run simple_design with invalid parameters: input_file='examples/data/1BC8.pdb', num_sequences=-1, temperature=2.0"

**Expected:** Validation errors or warnings about invalid parameters

### Prompt 19: Test Chain Specification
**Prompt:** "Use simple_design on examples/data/1BC8.pdb with chains='X Y Z' (non-existent chains)"

**Expected:** Error message about invalid chains or automatic chain detection

### Prompt 20: Test Output Directory
**Prompt:** "Run simple_design with input_file='examples/data/1BC8.pdb' and output_dir='./test_output' to save results to a specific location"

**Expected:** Successful execution with output saved to specified directory

---

## Testing Instructions

1. **Manual Testing**: Copy each prompt and paste into Claude Code CLI
2. **Record Results**: Note the actual responses for each prompt
3. **Check for Issues**: Look for:
   - Tools not found or not callable
   - Unexpected error messages
   - Missing or malformed responses
   - Performance issues (sync tools should complete quickly)
   - File path resolution problems

4. **Validation Criteria**:
   - ✅ Tool executes without errors
   - ✅ Returns expected JSON structure
   - ✅ Handles invalid inputs gracefully
   - ✅ File paths resolve correctly
   - ✅ Job workflow works end-to-end (submit → status → result)

5. **Performance Benchmarks**:
   - Sync tools (simple_design, sequence_scoring, etc.): < 30 seconds
   - Job submission: < 5 seconds (just submission, not completion)
   - Status/log queries: < 2 seconds

## Results Template

For each test, record:
```
Prompt #: [Number]
Status: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL
Response Time: [seconds]
Notes: [Any observations]
Issues: [Problems encountered]
```