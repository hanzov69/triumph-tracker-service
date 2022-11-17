[![Deploy triumph-tracker Container](https://github.com/hanzov69/triumph-tracker-service/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/hanzov69/triumph-tracker-service/actions/workflows/docker-image.yml)

# triumph-tracker-service

# Notes:
Build fails because of github wheels cache weirdness. Code is working, and `latest` container should work just fine.


# local docker
This is local, without vscode, ready to serve.
- `docker build -t ghcr.io/hanzov69/triumph-tracker:aiotest .`
- `docker run -p 8000:8000 ghcr.io/hanzov69/triumph-tracker:aiotest`
- open `http://127.0.0.1:8000`
- exec in to container, set API_KEY env, update manifest/clan_data

# devel docker
- To run/test this on your local environment, the easiest way is with vscode. Launch vscode and re-open in remote.
- Devcontainer will install requirements.txt automagically, but if this changes you may need to rebuild the container
- This includes node v18 and the live-css-editor server
- once launched, in terminal run `API_KEY="yourbungieykey" && export API_KEY`
- build manifest and player data
- - `cd ~/docker/app/backend`
- - `python manifest-destiny.py` this will grab the latest Bungie manifest
- - `python triumph-tracker.py` this will build the clan_data.sqlite3 db
- from `~/docker/app/frontend` run `flask run` This will start the app on `http://127.0.0.1:5000`
- For CSS editing in live, launch second terminal, go to `./docker/app/frontend/static` and run `live-css`
- - on browser side, make sure you have [live-css extension](https://chrome.google.com/webstore/detail/live-editor-for-css-less/ifhikkcafabcgolfjegfcgloomalapol)
- - on localhost page, launch extension, click "file" select `triumph-tracker.css` and you can live edit

# kube/argo
- make sure to define API_KEY correctly in the Secret yaml (will change in the future to do a value subst in argo)
- this will create the secret and expose it as a env var

## Todo Items
- Moved everything off to [Issues](https://github.com/hanzov69/triumph-tracker-service/issues)
