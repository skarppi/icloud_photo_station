# iCloud Photos Downloader for DSM

Helper scripts to repackage [iCloud Photos Downloader](https://github.com/icloud-photos-downloader/icloud_photos_downloader) Python library as a Synology DSM package for easy installation throught `Package Station`.

- A command-line tool to download all your iCloud photos and videos
- Runs on Synology DSM 7.x
- For other platforms (Linux, Windows, MacOS, Docker, etc), please go to original repository https://github.com/icloud-photos-downloader/icloud_photos_downloader

### Installation to Synology DSM

Ready made package is available:

- icloudpd-v1.23.4 [icloud_photo_station-1.23.4.spk](https://github.com/skarppi/icloud_photo_station/releases/download/v1.23.4/icloud_photo_station-1.23.4.spk)

- Or follow instructions below how to package SPK yourself from code with the latest available icloudpd library

```
    # Clone the repo somewhere
    git clone https://github.com/skarppi/icloud_photo_station.git
    cd icloud_photo_station

    # Create a SPK installation package containing virtualenv, python scripts and all necessary dependencies.
    cd spk
    sh build.sh
```

Manually install the spk in your DSM `Package Station`. After installation is complete you can set up `User-defined script` into `Task Scheduler` and set up scheduling. Notification emails for script output are handy to get notified if there are any problems.

```
    # temporary fix for permissions denied errors
    # https://github.com/icloud-photos-downloader/icloud_photos_downloader/issues/764
    export TMPDIR=$HOME/tmp

    source /volume1/@appstore/icloud_photo_station/env/bin/activate
    icloudpd \
        --username '<YOUR ICLOUD USERNAME>' \
        --password-provider keyring \
        --password-provider webui \
        --mfa-provider webui
        --auto-delete \
        --until-found 10 \
        --directory ./output/
```

Open WebUI at http://synology.local:8080 to input your password and two-factor authentication verification code when it's expired.

## Everything else

For more documentation, issues, or bugs go to https://github.com/icloud-photos-downloader/icloud_photos_downloader
