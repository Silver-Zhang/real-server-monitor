"""Tests for Slurm squeue output parsing."""

from pathlib import Path

from realmon.collectors.slurm import parse_squeue_output, is_slurm_available


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_squeue_output():
    sample = (FIXTURES_DIR / "squeue_sample.txt").read_text()
    jobs = parse_squeue_output(sample)

    assert len(jobs) == 3

    # First job
    assert jobs[0].job_id == "12345"
    assert jobs[0].user == "user1"
    assert jobs[0].state == "RUNNING"
    assert jobs[0].runtime == "1-02:30:00"
    assert jobs[0].alloc_cpus == "4"
    assert jobs[0].nodelist_or_reason == "(None)"
    assert jobs[0].job_name == "train_model"

    # Second job
    assert jobs[1].job_id == "12346"
    assert jobs[1].user == "user2"
    assert jobs[1].state == "PENDING"
    assert jobs[1].alloc_cpus == "8"
    assert jobs[1].nodelist_or_reason == "(Priority)"
    assert jobs[1].job_name == "data_process"

    # Third job
    assert jobs[2].job_id == "12347"
    assert jobs[2].user == "user1"
    assert jobs[2].state == "RUNNING"
    assert jobs[2].alloc_cpus == "16"
    assert jobs[2].nodelist_or_reason == "node[01-02]"
    assert jobs[2].job_name == "distributed_train"


def test_parse_squeue_empty():
    jobs = parse_squeue_output("")
    assert jobs == []


def test_parse_squeue_malformed():
    jobs = parse_squeue_output("not|enough|fields\n")
    assert jobs == []


def test_parse_squeue_with_blank_lines():
    sample = "\n12345|user1|RUNNING|1:00:00|1|4|node01|job1\n\n"
    jobs = parse_squeue_output(sample)
    assert len(jobs) == 1
    assert jobs[0].job_id == "12345"
