import tempfile
from pathlib import Path

from tools.system.error_handler import ErrorHandler


def test_file_not_found_recovery_creates_file(tmp_path: Path):
    handler = ErrorHandler(log_dir=str(tmp_path / "logs"))
    missing_file = tmp_path / "missing.txt"

    try:
        missing_file.read_text()
    except Exception as exc:
        result = handler.handle_error(exc, {"file_path": str(missing_file)})
        assert result["recovery_successful"] is True
        assert missing_file.exists()
