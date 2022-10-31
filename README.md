# triumph-tracker-service (less stable)

This branch isn't quite ready for prime time. 

To run/test this on your local environment, the easiest way is with vscode. Launch vscode and re-open in remote.

Otherwise, you should be able to get it running with .devcontainer/Dockerfile

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