"""Engine test conftest — pre-mock the DB modules so matrx_orm is never imported."""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

# Create mock modules for the entire db chain before anything imports them
_mock_matrx_orm = MagicMock()
_mock_matrx_utils = MagicMock()
_mock_db = MagicMock()
_mock_db_models = MagicMock()
_mock_app_db = MagicMock()
_mock_app_db_models = MagicMock()
_mock_app_db_custom = MagicMock()

sys.modules.setdefault("matrx_orm", _mock_matrx_orm)
sys.modules.setdefault("matrx_utils", _mock_matrx_utils)
sys.modules.setdefault("db", _mock_db)
sys.modules.setdefault("db.models", _mock_db_models)
sys.modules.setdefault("app.db", _mock_app_db)
sys.modules.setdefault("app.db.models", _mock_app_db_models)
sys.modules.setdefault("app.db.custom", _mock_app_db_custom)

# Expose a real AsyncMock for wf_core so tests can configure it
wf_core_mock = AsyncMock()
_mock_app_db_custom.wf_core = wf_core_mock
