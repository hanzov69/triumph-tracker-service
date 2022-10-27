import logging
from os import getenv
from pathlib import Path

import aiobungie

logging.basicConfig(
    format='{asctime} | {name} | {levelname} | {message}',
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
    level=logging.INFO
)

MANIFEST_DATA = Path(__file__).parent / 'manifest.sqlite3'
MANIFEST_VERSION = Path(__file__).parent / 'version.txt'
AIO_CLIENT = aiobungie.Client(getenv('API_KEY'))

async def check_manifest():
    '''Handles the manifest data'''
    # if it doesn't exist, go get it and save the version
    if not MANIFEST_DATA.exists():
        async with AIO_CLIENT.rest:
            await AIO_CLIENT.rest.download_manifest(path=MANIFEST_DATA.parent)
            remote_version = await AIO_CLIENT.rest.fetch_manifest_version()
        with MANIFEST_VERSION.open('w') as f:
            f.write(remote_version)
    # if it does exist, check the version against remote
    else:
        assert MANIFEST_VERSION.exists()
        with MANIFEST_VERSION.open() as f:
            local_version = f.read()
        async with AIO_CLIENT.rest:
            remote_version = await AIO_CLIENT.rest.fetch_manifest_version()
            # if remote version is different, assume newer data available and redownload
            if remote_version != local_version:
                MANIFEST_DATA.unlink()
                await AIO_CLIENT.rest.download_manifest(path=MANIFEST_DATA.parent)
                with MANIFEST_VERSION.open('w') as f:
                    f.write(remote_version)
    return

if __name__ == '__main__':
    AIO_CLIENT.run(check_manifest())
