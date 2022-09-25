[![Deploy triumph-tracker Container](https://github.com/hanzov69/triumph-tracker-service/actions/workflows/docker-image.yml/badge.svg?branch=main)](https://github.com/hanzov69/triumph-tracker-service/actions/workflows/docker-image.yml)

# triumph-tracker-service
Repo for a container based triumph-tracker for web thangs

## docker
### build
This is relative to the `docker/app` directory. Notice that tag is latest, semver can (should?) be used

`docker build -t ghcr.io/hanzov69/triumph-tracker:latest .`

### run
#### development
This is for mount your local directory in to `/usr/workspace`, which can be used for development.
Note that `/app` exists separately from this. 

`docker run -it -w /usr/workspace -v ${PWD}:/usr/workspace ghcr.io/hanzov69/triumph-tracker /bin/sh`
`python triumph-tracker.py`

#### local production test
`docker run -d -p 80:80 ghcr.io/hanzov69/triumph-tracker:latest`

## Files in docker/app
`config` config file for raids/users/urls/etc
`entry.sh` is a basic entrypoint script to run our python app (makes working directory stuff easy)
`requirements.txt` pip requirements
`triumph-cron` the cron job that gets symlinked in to our /etc/crontabs/root
`triumph-tracker.py` the workhorse of the show

## Files in kube
TBD