#!/usr/bin/env python3
"""Job management for long-running tasks in LigandMPNN MCP Server."""

import uuid
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import time

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobManager:
    """Manages asynchronous job execution for LigandMPNN tasks."""

    def __init__(self, jobs_dir: Path = None):
        self.jobs_dir = jobs_dir or Path(__file__).parent.parent.parent / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._running_jobs: Dict[str, subprocess.Popen] = {}

    def submit_job(
        self,
        script_path: str,
        args: Dict[str, Any],
        job_name: str = None
    ) -> Dict[str, Any]:
        """Submit a new job for background execution.

        Args:
            script_path: Path to the script to run
            args: Arguments to pass to the script
            job_name: Optional name for the job

        Returns:
            Dict with job_id and status
        """
        job_id = str(uuid.uuid4())[:8]
        job_dir = self.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Save job metadata
        metadata = {
            "job_id": job_id,
            "job_name": job_name or f"job_{job_id}",
            "script": script_path,
            "args": args,
            "status": JobStatus.PENDING.value,
            "submitted_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None
        }

        self._save_metadata(job_id, metadata)

        # Start job in background
        self._start_job(job_id, script_path, args, job_dir)

        return {
            "status": "submitted",
            "job_id": job_id,
            "message": f"Job submitted. Use get_job_status('{job_id}') to check progress."
        }

    def _start_job(self, job_id: str, script_path: str, args: Dict, job_dir: Path):
        """Start job execution in background thread."""
        def run_job():
            metadata = self._load_metadata(job_id)
            metadata["status"] = JobStatus.RUNNING.value
            metadata["started_at"] = datetime.now().isoformat()
            self._save_metadata(job_id, metadata)

            try:
                # Build command
                cmd = ["python", script_path]
                for key, value in args.items():
                    if value is not None:
                        if key == "inputs":  # Handle comma-separated list for batch
                            cmd.extend([f"--{key}", str(value)])
                        else:
                            cmd.extend([f"--{key}", str(value)])

                # Set output directory to job directory
                if "--output" not in cmd:
                    cmd.extend(["--output", str(job_dir / "output")])

                # Run script
                log_file = job_dir / "job.log"
                with open(log_file, 'w') as log:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        cwd=str(Path(script_path).parent.parent)
                    )
                    self._running_jobs[job_id] = process
                    process.wait()

                # Update status
                if process.returncode == 0:
                    metadata["status"] = JobStatus.COMPLETED.value
                    # Try to collect output information
                    output_dir = job_dir / "output"
                    if output_dir.exists():
                        metadata["output_dir"] = str(output_dir)
                else:
                    metadata["status"] = JobStatus.FAILED.value
                    metadata["error"] = f"Process exited with code {process.returncode}"

            except Exception as e:
                metadata["status"] = JobStatus.FAILED.value
                metadata["error"] = str(e)
                if hasattr(logger, 'error'):
                    logger.error(f"Job {job_id} failed: {e}")
                else:
                    print(f"Job {job_id} failed: {e}")

            finally:
                metadata["completed_at"] = datetime.now().isoformat()
                self._save_metadata(job_id, metadata)
                self._running_jobs.pop(job_id, None)

        thread = threading.Thread(target=run_job, daemon=True)
        thread.start()

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a submitted job."""
        metadata = self._load_metadata(job_id)
        if not metadata:
            return {"status": "error", "error": f"Job {job_id} not found"}

        result = {
            "job_id": job_id,
            "job_name": metadata.get("job_name"),
            "status": metadata["status"],
            "submitted_at": metadata.get("submitted_at"),
            "started_at": metadata.get("started_at"),
            "completed_at": metadata.get("completed_at")
        }

        if metadata["status"] == JobStatus.FAILED.value:
            result["error"] = metadata.get("error")

        if metadata["status"] == JobStatus.COMPLETED.value and "output_dir" in metadata:
            result["output_dir"] = metadata["output_dir"]

        return result

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Get results of a completed job."""
        metadata = self._load_metadata(job_id)
        if not metadata:
            return {"status": "error", "error": f"Job {job_id} not found"}

        if metadata["status"] != JobStatus.COMPLETED.value:
            return {
                "status": "error",
                "error": f"Job not completed. Current status: {metadata['status']}"
            }

        # Load output information
        job_dir = self.jobs_dir / job_id
        output_dir = job_dir / "output"

        result = {
            "status": "success",
            "job_id": job_id,
            "completed_at": metadata.get("completed_at"),
            "output_dir": str(output_dir) if output_dir.exists() else None
        }

        # Try to gather information about generated files
        if output_dir.exists():
            files = []
            for file_path in output_dir.rglob("*"):
                if file_path.is_file():
                    files.append({
                        "path": str(file_path),
                        "relative_path": str(file_path.relative_to(output_dir)),
                        "size": file_path.stat().st_size
                    })
            result["generated_files"] = files
            result["total_files"] = len(files)

        return result

    def get_job_log(self, job_id: str, tail: int = 50) -> Dict[str, Any]:
        """Get log output from a job."""
        job_dir = self.jobs_dir / job_id
        log_file = job_dir / "job.log"

        if not log_file.exists():
            return {"status": "error", "error": f"Log not found for job {job_id}"}

        try:
            with open(log_file) as f:
                lines = f.readlines()

            return {
                "status": "success",
                "job_id": job_id,
                "log_lines": lines[-tail:] if tail > 0 else lines,
                "total_lines": len(lines)
            }
        except Exception as e:
            return {"status": "error", "error": f"Failed to read log: {e}"}

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running job."""
        if job_id in self._running_jobs:
            try:
                self._running_jobs[job_id].terminate()
                # Give it a moment to terminate gracefully
                time.sleep(1)
                if self._running_jobs[job_id].poll() is None:
                    # Force kill if still running
                    self._running_jobs[job_id].kill()

                metadata = self._load_metadata(job_id)
                if metadata:
                    metadata["status"] = JobStatus.CANCELLED.value
                    metadata["completed_at"] = datetime.now().isoformat()
                    self._save_metadata(job_id, metadata)

                return {"status": "success", "message": f"Job {job_id} cancelled"}
            except Exception as e:
                return {"status": "error", "error": f"Failed to cancel job: {e}"}

        # Check if job exists and is not running
        metadata = self._load_metadata(job_id)
        if not metadata:
            return {"status": "error", "error": f"Job {job_id} not found"}

        if metadata["status"] in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
            return {"status": "error", "error": f"Job {job_id} already finished with status: {metadata['status']}"}

        return {"status": "error", "error": f"Job {job_id} not running"}

    def list_jobs(self, status: Optional[str] = None) -> Dict[str, Any]:
        """List all jobs, optionally filtered by status."""
        jobs = []
        try:
            for job_dir in self.jobs_dir.iterdir():
                if job_dir.is_dir():
                    metadata = self._load_metadata(job_dir.name)
                    if metadata:
                        if status is None or metadata["status"] == status:
                            jobs.append({
                                "job_id": metadata["job_id"],
                                "job_name": metadata.get("job_name"),
                                "status": metadata["status"],
                                "submitted_at": metadata.get("submitted_at"),
                                "script": metadata.get("script"),
                            })
        except Exception as e:
            return {"status": "error", "error": f"Failed to list jobs: {e}"}

        # Sort by submission time, most recent first
        jobs.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)

        return {"status": "success", "jobs": jobs, "total": len(jobs)}

    def _save_metadata(self, job_id: str, metadata: Dict):
        """Save job metadata to disk."""
        meta_file = self.jobs_dir / job_id / "metadata.json"
        meta_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Failed to save metadata for job {job_id}: {e}")

    def _load_metadata(self, job_id: str) -> Optional[Dict]:
        """Load job metadata from disk."""
        meta_file = self.jobs_dir / job_id / "metadata.json"
        if meta_file.exists():
            try:
                with open(meta_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load metadata for job {job_id}: {e}")
        return None


# Global job manager instance
job_manager = JobManager()