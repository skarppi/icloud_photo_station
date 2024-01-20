# iCloud Photos Downloader for DSM

- A command-line tool to download all your iCloud photos and videos
- Runs on Synology DSM 7.x
- For other platforms (Linux, Windows, MacOS, Docker), please go to original repository https://github.com/icloud-photos-downloader

### Installation to Synology DSM

Ready made packages are available:

- For DSM 7.x [icloud_photo_station-0.4.0.spk](https://github.com/skarppi/icloud_photo_station/releases/download/v0.3.0/icloud_photo_station-0.4.0.spk)

- Or follow instructions below how to package SPK yourself from code. Use ```dsm6``` branch for DSM 6.x but iCloud.

```
    # Clone the repo somewhere
    git clone https://github.com/skarppi/icloud_photo_station.git
    cd icloud_photo_station

    # Create a SPK installation package containing virtualenv, python scripts and all necessary dependencies.
    cd spk
    sh build.sh
```

Manually install the spk in your DSM `Package Station`. After installation is complete you can set up `User-defined script` into `Task Scheduler` and set up scheduling. Notification emails for script output are handy to get notified when two-factor authentication has expired.

```
    source /volume1/@appstore/icloud_photo_station/env/bin/activate
    python /volume1/@appstore/icloud_photo_station/app/icloudpd.py \
        --username '<YOUR ICLOUD USERNAME>' \
        --password '<YOUR ICLOUD PASSWORD>' \
        --auto-delete \
        --until-found 10 \
        --directory ./output/
```

If your iCloud account has two-factor authentication enabled, SSH to Synology box and run the script manually first time in order to input the verification code. This step needs to be repeated every once in a while when the authentication expires.

## Features

- Three modes of operation:
  - **Copy** - download new photos from iCloud (default mode)
  - **Sync** - download new photos from iCloud and delete local files that were removed in iCloud (`--auto-delete` option)
  - **Move** - download new photos from iCloud and delete photos in iCloud (`--delete-after-download` option)
- Support for Live Photos (image and video as separate files)
- Automatic de-duplication of photos with the same name
- One time download and an option to monitor for iCloud changes continuously (`--watch-with-interval` option)
- Optimizations for incremental runs (`--until-found` and `--recent` options)
- Photo meta data (EXIF) updates (`--set-exif-datetime` option)
- ... and many more (use `--help` option to get full list)

## Experimental Mode

Some changes are added to the experimental mode before they graduate into the main package. [Details](EXPERIMENTAL.md)

## Usage

To keep your iCloud photo collection synchronized to your local system:

```
icloudpd --directory /data --username my@email.address --watch-with-interval 3600
```

- Synchronization logic can be adjusted with command-line parameters. Run `icloudpd --help` to get full list.

To independently create and authorize a session (and complete 2SA/2FA validation if needed) on your local system:

```
icloudpd --username my@email.address --password my_password --auth-only
```

- This feature can also be used to check and verify that the session is still authenticated. 

## FAQ

Nuances of working with the iCloud or a specific operating system are collected in the [FAQ](FAQ.md). Also, check [Issues](https://github.com/icloud-photos-downloader/icloud_photos_downloader/issues).

## Contributing

Want to contribute to iCloud Photos Downloader? Awesome! Check out the [contributing guidelines](CONTRIBUTING.md) to get involved.
