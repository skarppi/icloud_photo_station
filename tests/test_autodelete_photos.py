from unittest import TestCase
from vcr import VCR
import os
import shutil
import pytest
from click.testing import CliRunner
from icloudpd.base import main
import inspect

vcr = VCR(decode_compressed_response=True, record_mode="new_episodes")


class AutodeletePhotosTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_autodelete_photos(self):
        base_dir = os.path.normpath(f"tests/fixtures/Photos/{inspect.stack()[0][3]}")
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        os.makedirs(base_dir)

        # create some empty files that should be deleted
        os.makedirs(os.path.join(base_dir, "2018/07/30/"))
        open(os.path.join(base_dir, "2018/07/30/IMG_7406.MOV"), "a").close()
        os.makedirs(os.path.join(base_dir, "2018/07/26/"))
        open(os.path.join(base_dir, "2018/07/26/IMG_7383.PNG"), "a").close()
        os.makedirs(os.path.join(base_dir, "2018/07/12/"))
        open(os.path.join(base_dir, "2018/07/12/IMG_7190.JPG"), "a").close()
        open(os.path.join(base_dir, "2018/07/12/IMG_7190-medium.JPG"), "a").close()

        # Should not be deleted
        open(os.path.join(base_dir, "2018/07/30/IMG_7407.JPG"), "a").close()
        open(os.path.join(base_dir, "2018/07/30/IMG_7407-original.JPG"), "a").close()

        with vcr.use_cassette("tests/vcr_cassettes/autodelete_photos.yml"):
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
                    "0",
                    "--skip-videos",
                    "--auto-delete",
                    "-d",
                    base_dir,
                ],
            )
            self.assertIn("DEBUG    Looking up all photos from album All Photos...", self._caplog.text)
            self.assertIn(
                f"INFO     Downloading 0 original photos to {base_dir} ...",
                self._caplog.text,
            )
            self.assertIn(
                "INFO     All photos have been downloaded!", self._caplog.text
            )
            self.assertIn(
                "INFO     Deleting any files found in 'Recently Deleted'...",
                self._caplog.text,
            )

            self.assertIn(
                "INFO     Deleting any files found in 'Recently Deleted'...",
                self._caplog.text,
            )

            self.assertIn(
                f"INFO     Deleting {os.path.join(base_dir, os.path.normpath('2018/07/30/IMG_7406.MOV'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"INFO     Deleting {os.path.join(base_dir, os.path.normpath('2018/07/26/IMG_7383.PNG'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"INFO     Deleting {os.path.join(base_dir, os.path.normpath('2018/07/12/IMG_7190.JPG'))}",
                self._caplog.text,
            )
            self.assertIn(
                f"INFO     Deleting {os.path.join(base_dir, os.path.normpath('2018/07/12/IMG_7190-medium.JPG'))}",
                self._caplog.text,
            )

            self.assertNotIn("IMG_7407.JPG", self._caplog.text)
            self.assertNotIn("IMG_7407-original.JPG", self._caplog.text)

            assert result.exit_code == 0
