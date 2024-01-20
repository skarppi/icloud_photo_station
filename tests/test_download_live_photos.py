from unittest import TestCase
from vcr import VCR
import os
import sys
import shutil
import pytest
import mock
import datetime
from mock import call, ANY
from click.testing import CliRunner
import piexif
from piexif._exceptions import InvalidImageDataError
from pyicloud_ipd.services.photos import PhotoAsset, PhotoAlbum, PhotosService
from pyicloud_ipd.base import PyiCloudService
from pyicloud_ipd.exceptions import PyiCloudAPIResponseException
from requests.exceptions import ConnectionError
from icloudpd.base import main
from tests.helpers import path_from_project_root, print_result_exception, recreate_path
import inspect
import glob

vcr = VCR(decode_compressed_response=True)

class DownloadLivePhotoTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog
        self.root_path = path_from_project_root(__file__)
        self.fixtures_path = os.path.join(self.root_path, "fixtures")
        self.vcr_path = os.path.join(self.root_path, "vcr_cassettes")

    def test_skip_existing_downloads_for_live_photos(self):
        base_dir = os.path.join(self.fixtures_path, inspect.stack()[0][3])
        cookie_dir = os.path.join(base_dir, "cookie")
        data_dir = os.path.join(base_dir, "data")

        for dir in [base_dir, cookie_dir, data_dir]:
            recreate_path(dir)

        files_to_download = [
            "2020/11/04/IMG_0516.HEIC",
            "2020/11/04/IMG_0514.HEIC",
            "2020/11/04/IMG_0514_HEVC.MOV",
            "2020/11/04/IMG_0512.HEIC",
            "2020/11/04/IMG_0512_HEVC.MOV"
        ]

        with vcr.use_cassette(os.path.join(self.vcr_path, "download_live_photos.yml")):
            # Pass fixed client ID via environment variable
            runner = CliRunner(env={
                "CLIENT_ID": "DE309E26-942E-11E8-92F5-14109FE0B321"
            })
            result = runner.invoke(
                main,
                [
                    "--username",
                    "jdoe@gmail.com",
                    "--password",
                    "password1",
                    "--recent",
                    "3",
                    "--no-progress-bar",
                    "--threads-num",
                    1,
                    "-d",
                    data_dir,
                    "--cookie-directory",
                    cookie_dir
                ],
            )
            print_result_exception(result)

            self.assertIn(
                f"DEBUG    Downloading {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0514_HEVC.MOV'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"DEBUG    Downloading {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0514.HEIC'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"DEBUG    Downloading {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0516.HEIC'))}",
                self._caplog.text,
            )
            self.assertIn(
                "INFO     All photos have been downloaded", self._caplog.text
            )
            assert result.exit_code == 0

        files_in_result = glob.glob(os.path.join(data_dir, "**/*.*"), recursive=True)

        assert sum(1 for _ in files_in_result) == len(files_to_download)

        for file_name in files_to_download:
            assert os.path.exists(os.path.join(data_dir, os.path.normpath(file_name))), f"file {file_name} expected, but not found"

    def test_skip_existing_live_photodownloads(self):
        base_dir = os.path.join(self.fixtures_path, inspect.stack()[0][3])
        cookie_dir = os.path.join(base_dir, "cookie")
        data_dir = os.path.join(base_dir, "data")

        for dir in [base_dir, cookie_dir, data_dir]:
            recreate_path(dir)

        files_to_create = [
            ("2020/11/04/IMG_0516.HEIC", 1651485),
            ("2020/11/04/IMG_0514_HEVC.MOV", 3951774),
        ]

        files_to_download = [
            "2020/11/04/IMG_0514.HEIC",
            "2020/11/04/IMG_0512.HEIC",
            "2020/11/04/IMG_0512_HEVC.MOV"
        ]

        # simulate that some expected files are there with correct sizes
        os.makedirs(os.path.join(data_dir, "2020/11/04"))
        # one photo and one movie are already there and should be skipped
        # Create dummies with the correct size
        for (file_name, file_size) in files_to_create:
            with open(os.path.join(data_dir, file_name), "a") as f:
                f.truncate(file_size)

        with vcr.use_cassette(os.path.join(self.vcr_path, "download_live_photos.yml")):
            # Pass fixed client ID via environment variable
            runner = CliRunner(env={
                "CLIENT_ID": "DE309E26-942E-11E8-92F5-14109FE0B321"
            })
            result = runner.invoke(
                main,
                [
                    "--username",
                    "jdoe@gmail.com",
                    "--password",
                    "password1",
                    "--recent",
                    "3",
                    "--no-progress-bar",
                    "--threads-num",
                    1,
                    "-d",
                    data_dir,
                    "--cookie-directory",
                    cookie_dir,
                ],
            )
            print_result_exception(result)

            self.assertIn(
                "DEBUG    Looking up all photos and videos from album All Photos...", self._caplog.text
            )
            self.assertIn(
                f"INFO     Downloading 3 original photos and videos to {data_dir} ...",
                self._caplog.text,
            )
            self.assertIn(
                f"DEBUG    Downloading {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0514.HEIC'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"DEBUG    {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0514_HEVC.MOV'))} already exists",
                self._caplog.text,
            )
            self.assertIn(
                f"DEBUG    Downloading {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0514.HEIC'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"DEBUG    {os.path.join(data_dir, os.path.normpath('2020/11/04/IMG_0516.HEIC'))} already exists",
                self._caplog.text,
            )
            self.assertIn(
                "INFO     All photos have been downloaded", self._caplog.text
            )
            assert result.exit_code == 0


        files_in_result = glob.glob(os.path.join(data_dir, "**/*.*"), recursive=True)

        assert sum(1 for _ in files_in_result) == len(files_to_download) + len(files_to_create)

        for file_name in files_to_download + ([file_name for (file_name, _) in files_to_create]):
            assert os.path.exists(os.path.join(data_dir, os.path.normpath(file_name))), f"file {file_name} expected, but not found"

    def test_skip_existing_live_photo_print_filenames(self):
        base_dir = os.path.join(self.fixtures_path, inspect.stack()[0][3])
        cookie_dir = os.path.join(base_dir, "cookie")
        data_dir = os.path.join(base_dir, "data")

        for dir in [base_dir, cookie_dir, data_dir]:
            recreate_path(dir)

        files_to_create = [
            ("2020/11/04/IMG_0516.HEIC", 1651485),
            ("2020/11/04/IMG_0514_HEVC.MOV", 3951774),
        ]

        files_to_download = [
            "2020/11/04/IMG_0514.HEIC",
            "2020/11/04/IMG_0512.HEIC",
            "2020/11/04/IMG_0512_HEVC.MOV"
        ]

        # simulate that some expected files are there with correct sizes
        os.makedirs(os.path.join(data_dir, "2020/11/04"))
        # one photo and one movie are already there and should be skipped
        # Create dummies with the correct size
        for (file_name, file_size) in files_to_create:
            with open(os.path.join(data_dir, file_name), "a") as f:
                f.truncate(file_size)

        with vcr.use_cassette(os.path.join(self.vcr_path, "download_live_photos.yml")):
            # Pass fixed client ID via environment variable
            runner = CliRunner(env={
                "CLIENT_ID": "DE309E26-942E-11E8-92F5-14109FE0B321"
            })
            result = runner.invoke(
                main,
                [
                    "--username",
                    "jdoe@gmail.com",
                    "--password",
                    "password1",
                    "--recent",
                    "3",
                    "--no-progress-bar",
                    "--threads-num",
                    1,
                    "--only-print-filenames",
                    "-d",
                    data_dir,
                    "--cookie-directory",
                    cookie_dir,
                ],
            )
            print_result_exception(result)

            filenames = result.output.splitlines()

            print (filenames)

            assert len(filenames) == 3

            self.assertEqual(
                os.path.join(data_dir, os.path.normpath("2020/11/04/IMG_0514.HEIC")),
                filenames[0]
            )
            self.assertEqual(
                os.path.join(data_dir, os.path.normpath("2020/11/04/IMG_0512.HEIC")),
                filenames[1]
            )
            self.assertEqual(
                os.path.join(data_dir, os.path.normpath("2020/11/04/IMG_0512_HEVC.MOV")),
                filenames[2]
            )

            # Double check that a mocked file does not get listed again. It's already there!
            assert "2020/11/04/IMG_0514_HEVC.MOV" not in filenames

            assert result.exit_code == 0

        files_in_result = glob.glob(os.path.join(data_dir, "**/*.*"), recursive=True)

        assert sum(1 for _ in files_in_result) == len(files_to_create)

        for file_name in ([file_name for (file_name, _) in files_to_create]):
            assert os.path.exists(os.path.join(data_dir, os.path.normpath(file_name))), f"file {file_name} expected, but not found"
