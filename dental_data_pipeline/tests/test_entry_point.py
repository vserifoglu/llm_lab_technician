
import pytest
from unittest.mock import patch, MagicMock
import sys
from dental_data_pipeline.main import main

def test_main_cli_execution_valid_path(tmp_path):
    """Test that main() runs without error when given a valid path."""
    d = tmp_path / "data"
    d.mkdir()
    test_args = ["main.py", "--data-dir", str(d)]
    
    with patch("sys.argv", test_args):
        with patch("dental_data_pipeline.main.ThreadPoolExecutor") as mock_executor:
            mock_executor.return_value.__enter__.return_value.map.return_value = []
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
            except Exception as e:
                pytest.fail(f"main() raised exception: {e}")

def test_main_cli_no_args():
    with patch("sys.argv", ["main.py"]):
        with pytest.raises(SystemExit):
             main()
