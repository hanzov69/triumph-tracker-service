# TODO List

## Frontend
- [ ] currently populating each cell with ajax call, this is expensive and with slow worker looks bad
- [ ] check for freshness of manifest on page load- if stale, re-pull
- [ ] as above, but for clan_data
- [ ] PWA? (do I hate myself?)
- [ ] needs CSS / javascript to make pretty
- [ ] give some CRUD to frontend to allow adding/removing `players`
- [ ] use cache for values to hide ajax slowness?
- [x] row highlight on mouseover for readability
- [x] toggle cell highlighting for incomplete

## Backend
- [ ] read in `players` from DB versus hardcode
- [ ] as above, but for raids


## Container Stuff
- [x] Store container in github registry
- [ ] stretch: discord shit?
- [x] nginx to host local files
- [x] nginx acting as reverse proxy for subdomain

## Infra Stuff
- do substitution on API_KEY 

## Podspec stuff
- [x] deploying from github registry

## CI/CD Stuff
- [x] github actions? _yup, added container builder and registry stuff_
- [x] gitops deploys _used argocd_
- [ ] argo could benefit from PV/PVC, might be worth moving to hive
- [ ] update argo for `aiotest` so it's smooth with merged to `main`
- [ ] update actions to actually do versioning, create releases?

## General Stuff
- [ ] Should be using Github Issues instead of this TODO?

