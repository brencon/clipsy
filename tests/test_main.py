"""Tests for __main__.py CLI and LaunchAgent functions."""

from unittest.mock import MagicMock, patch

import pytest

from clipsy.__main__ import (
    PLIST_NAME,
    check_status,
    create_plist,
    get_clipsy_path,
    install_launchagent,
    main,
    uninstall_launchagent,
)


class TestCreatePlist:
    def test_contains_label(self):
        plist = create_plist("/usr/local/bin/clipsy")
        assert "<string>com.clipsy.app</string>" in plist

    def test_contains_clipsy_path(self):
        plist = create_plist("/opt/homebrew/bin/clipsy")
        assert "<string>/opt/homebrew/bin/clipsy</string>" in plist

    def test_contains_run_argument(self):
        plist = create_plist("/usr/local/bin/clipsy")
        assert "<string>run</string>" in plist

    def test_contains_keep_alive(self):
        plist = create_plist("/usr/local/bin/clipsy")
        assert "<key>KeepAlive</key>" in plist
        assert "<true/>" in plist

    def test_contains_log_path(self):
        plist = create_plist("/usr/local/bin/clipsy")
        assert "clipsy.log</string>" in plist

    def test_valid_xml(self):
        plist = create_plist("/usr/local/bin/clipsy")
        assert plist.startswith("<?xml version=")
        assert "</plist>" in plist


class TestGetClipsyPath:
    @patch("shutil.which", return_value="/usr/local/bin/clipsy")
    def test_returns_which_path(self, _mock_which):
        assert get_clipsy_path() == "/usr/local/bin/clipsy"

    @patch("shutil.which", return_value=None)
    def test_falls_back_to_python_module(self, _mock_which):
        path = get_clipsy_path()
        assert "-m clipsy" in path


class TestInstallLaunchAgent:
    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    @patch("clipsy.__main__.LAUNCHAGENT_DIR")
    @patch("clipsy.__main__.ensure_dirs")
    @patch("clipsy.__main__.get_clipsy_path", return_value="/usr/local/bin/clipsy")
    def test_install_success(self, _mock_path, _mock_dirs, mock_la_dir, mock_plist, mock_run):
        mock_plist.exists.return_value = False
        mock_run.return_value = MagicMock(returncode=0)
        assert install_launchagent() == 0

    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    @patch("clipsy.__main__.LAUNCHAGENT_DIR")
    @patch("clipsy.__main__.ensure_dirs")
    @patch("clipsy.__main__.get_clipsy_path", return_value="/usr/local/bin/clipsy")
    def test_install_failure(self, _mock_path, _mock_dirs, mock_la_dir, mock_plist, mock_run):
        mock_plist.exists.return_value = False
        mock_run.return_value = MagicMock(returncode=1, stderr="load failed")
        assert install_launchagent() == 1

    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    @patch("clipsy.__main__.LAUNCHAGENT_DIR")
    @patch("clipsy.__main__.ensure_dirs")
    @patch("clipsy.__main__.get_clipsy_path", return_value="/usr/local/bin/clipsy")
    def test_install_unloads_existing(self, _mock_path, _mock_dirs, mock_la_dir, mock_plist, mock_run):
        mock_plist.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        install_launchagent()
        # First call should be unload, second should be load
        assert mock_run.call_count == 2


class TestUninstallLaunchAgent:
    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    def test_uninstall_not_installed(self, mock_plist, _mock_run):
        mock_plist.exists.return_value = False
        assert uninstall_launchagent() == 0

    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    def test_uninstall_success(self, mock_plist, mock_run):
        mock_plist.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        assert uninstall_launchagent() == 0
        mock_plist.unlink.assert_called_once()


class TestCheckStatus:
    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    def test_running(self, mock_plist, mock_run):
        mock_plist.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        assert check_status() == 0

    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    def test_not_running_installed(self, mock_plist, mock_run):
        mock_plist.exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1)
        assert check_status() == 1

    @patch("clipsy.__main__.subprocess.run")
    @patch("clipsy.__main__.PLIST_PATH")
    def test_not_running_not_installed(self, mock_plist, mock_run):
        mock_plist.exists.return_value = False
        mock_run.return_value = MagicMock(returncode=1)
        assert check_status() == 1


class TestCLIParsing:
    @patch("clipsy.__main__.install_launchagent", return_value=0)
    def test_default_installs(self, mock_install):
        with patch("sys.argv", ["clipsy"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            mock_install.assert_called_once()

    @patch("clipsy.__main__.uninstall_launchagent", return_value=0)
    def test_uninstall_command(self, mock_uninstall):
        with patch("sys.argv", ["clipsy", "uninstall"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            mock_uninstall.assert_called_once()

    @patch("clipsy.__main__.check_status", return_value=0)
    def test_status_command(self, mock_status):
        with patch("sys.argv", ["clipsy", "status"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            mock_status.assert_called_once()

    @patch("clipsy.__main__.run_app")
    def test_run_command(self, mock_run):
        with patch("sys.argv", ["clipsy", "run"]):
            main()
            mock_run.assert_called_once()
