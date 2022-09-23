# triumph-tracker-service
Repo for a container based triumph-tracker for web thangs

## Temp - docker build
`docker build -f Slim-Bullseye.Dockerfile -t python-geckodriver .`
or
`docker build -f Alpine.Dockerfile -t python-geckodriver .`

## Temp - docker run
`docker run -it -w /usr/workspace -v ${PWD}:/usr/workspace python-geckodriver /bin/sh`
`python triumph-tracker.py`