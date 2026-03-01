"""Engine test conftest — pre-mock the DB modules so matrx_orm is never imported."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# Create mock modules for the entire db chain before anything imports them
_mock_db = MagicMock()
_mock_db_models = MagicMock()
_mock_app_db = MagicMock()
_mock_app_db_models = MagicMock()

sys.modules.setdefault("matrx_orm", MagicMock())
sys.modules.setdefault("db", _mock_db)
sys.modules.setdefault("db.models", _mock_db_models)
sys.modules.setdefault("app.db", _mock_app_db)
sys.modules.setdefault("app.db.models", _mock_app_db_models)
