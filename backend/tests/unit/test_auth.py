"""Auth unit tests."""
import pytest
from app.security.jwt import create_access_token, verify_access_token, create_refresh_token, verify_refresh_token
from app.security.password import hash_password, verify_password, validate_password_strength


def test_access_token_roundtrip():
    token = create_access_token("test-user-id")
    result = verify_access_token(token)
    assert result == "test-user-id"


def test_refresh_token_roundtrip():
    token = create_refresh_token("test-user-id")
    result = verify_refresh_token(token)
    assert result == "test-user-id"


def test_access_token_is_not_refresh():
    token = create_access_token("test-user-id")
    result = verify_refresh_token(token)
    assert result is None


def test_invalid_token_returns_none():
    result = verify_access_token("totally.invalid.token")
    assert result is None


def test_password_hash_and_verify():
    pwd = "SecurePass@123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_password_strength_valid():
    assert validate_password_strength("SecurePass@123") is True


def test_password_strength_too_short():
    assert validate_password_strength("Ab1!") is False


def test_password_strength_no_uppercase():
    assert validate_password_strength("alllowercase1!") is False


def test_password_strength_no_lowercase():
    assert validate_password_strength("ALLUPPERCASE1!") is False


def test_password_strength_no_special():
    assert validate_password_strength("NoSpecialChar1") is False
