# Unit Tests for ChatSpace

Automated tests for validating core functionality and catching regressions in the ChatSpace messaging platform.

---

## 📋 Test Coverage

| File | Module | Tests |
|------|--------|-------|
| `test_server.py` | `server/server.py` | Server initialization, user management, session handling |
| `test_encryption.py` | `server/encryption.py` | RSA/AES encryption, key exchange, cryptographic operations |
| `test_gui.py` | `client/gui.py` | GUI components, validation, message handling |

---

## 🚀 Quick Start

### Install Dependencies
```bash
conda activate base  # or: source venv/bin/activate
pip install pytest pytest-cov
```

### Run All Tests
```bash
cd /Users/nami-macos/Documents/GitHub/chatroom-project
pytest tests/ -v
```

---

## 🎯 Common Commands

```bash
# All tests with output
pytest tests/ -v -s

# Specific test file
pytest tests/test_server.py -v

# Specific test method
pytest tests/test_server.py::TestChatServer::test_user_management -v

# With coverage report
pytest tests/ --cov=server --cov=client --cov-report=html
open htmlcov/index.html

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

---

## 📊 Expected Output

```
tests/test_server.py::TestChatServer::test_server_initialization PASSED
✅ Server initialization test passed

tests/test_server.py::TestChatServer::test_user_management PASSED
✅ User management test passed

tests/test_server.py::TestChatServer::test_user_lookup PASSED
✅ User lookup test passed

tests/test_server.py::test_simple_math PASSED
✅ Simple math test passed

========================= 4 passed in 0.15s =========================
```

---

**Documentation**: https://docs.pytest.org/  
**Last updated**: December 2025