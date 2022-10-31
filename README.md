# triumph-tracker-service (less stable)

This branch isn't quite ready for prime time. 

# warnings
Currently, the manifest and clan_data are manually triggered. This will change soon.

# local docker
This is local, without vscode, ready to serve.
- `docker build -t ghcr.io/hanzov69/triumph-tracker:aiotest .`
- `docker run -p 8000:8000 ghcr.io/hanzov69/triumph-tracker:aiotest`
- open `http://127.0.0.1:8000`
- exec in to container, set API_KEY env, update manifest/clan_data

# devel docker
To run/test this on your local environment, the easiest way is with vscode. Launch vscode and re-open in remote.

Once in the container, 
- `cd /docker/app/`
- `pip3 install -r requirements.txt`
- `cd /docker/app/backend`
- `python manifest-destiny.py` this will grab the latest Bungie manifest
- `python triumph-tracker.py` this will build the clan_data.sqlite3 db
- `cd /docker/app/frontend/`
- `flask run` This will start the app on `http://127.0.0.1:5000`

## ToDo - General
- need to update `Dockerfile`
- probably freshen up .gitignore

## ToDo - Frontend
- Create `About` route, show credits, version, manifest/clan_data freshness
- Lots of CSS work
- Better javascript, allow filtering, hiding complete, whatnot
- Frontend refresh stale backend data? (better than cron)