"""Tests for command sanitize utility."""

from realmon.utils.command_sanitize import sanitize_command


def test_sanitize_password_flag():
    cmd = "python train.py --password 123456 --lr 0.01"
    result = sanitize_command(cmd)
    assert "123456" not in result
    assert "***" in result
    assert "--lr 0.01" in result


def test_sanitize_token_flag():
    cmd = "python train.py --token abcdefg123 --epochs 10"
    result = sanitize_command(cmd)
    assert "abcdefg123" not in result
    assert "***" in result
    assert "--epochs 10" in result


def test_sanitize_api_key_flag():
    cmd = "curl --api_key sk-abc123 https://api.example.com"
    result = sanitize_command(cmd)
    assert "sk-abc123" not in result
    assert "***" in result


def test_sanitize_secret_flag():
    cmd = "app --secret mysecretvalue --verbose"
    result = sanitize_command(cmd)
    assert "mysecretvalue" not in result
    assert "***" in result
    assert "--verbose" in result


def test_sanitize_credential_flag():
    cmd = "tool --credential cred123 --output /tmp/out"
    result = sanitize_command(cmd)
    assert "cred123" not in result
    assert "***" in result


def test_sanitize_env_style():
    cmd = "****** python script.py"
    result = sanitize_command(cmd)
    assert "hunter2" not in result
    assert "***" in result


def test_sanitize_no_sensitive():
    cmd = "python train.py --lr 0.01 --epochs 100"
    result = sanitize_command(cmd)
    assert result == cmd


def test_sanitize_multiple_sensitive():
    cmd = "app --token abc --password xyz --key 123"
    result = sanitize_command(cmd)
    assert "abc" not in result
    assert "xyz" not in result
    assert "123" not in result
    assert result.count("***") == 3


def test_sanitize_equals_form():
    cmd = "app --token=abc123 --******"
    result = sanitize_command(cmd)
    assert "abc123" not in result
    assert "xyz789" not in result


def test_sanitize_case_insensitive():
    cmd = "app --TOKEN abc123 --Password xyz"
    result = sanitize_command(cmd)
    assert "abc123" not in result
    assert "xyz" not in result
