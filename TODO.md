# TODO List

## Code
- ~~[x] Selenium 4 `DeprecationWarning: executable_path has been deprecated, please pass in a Service object` _fixed_~~
- ~~[x] Selenium 4 `DeprecationWarning: service_log_path has been deprecated, please pass in a Service object`~~
- ~~[x] Add some args support (quiet)~~
- ~~[x] output in json (--jsonout or -j)~~
- ~~[x] output in html (--htmlout or -w)~~
- [ ] (frontend) currently populating each cell with ajax call, this is expensive and with slow worker looks bad
- [ ] (frontend) check for freshness of manifest on page load- if stale, re-pull
- [ ] (frontend) as above, but for clan_data
- [ ] (frontend) PWA? (do I hate myself?)
- [ ] (frontend) needs CSS / javascript to make pretty
- [ ] (frontend) give some CRUD to frontend to allow adding/removing `players`
- [ ] (backend) read in `players` from DB versus hardcode
- [ ] (backend) as above, but for raids
- [ ] (frontend) use cache for values to hide ajax slowness?

## Container Stuff
- ~~[x] Create Container that can run selenium based on https://github.com/m9brady/triumph-tracker~~
- ~~[x] selenium job as cron/timed event~~
- ~~[x] display pretty page with stats from selenium job _(pretty might be a stretch..)_~~
- [x] Store container in github registry
- [ ] stretch: discord shit?
- [x] nginx to host local files
- [x] nginx acting as reverse proxy for subdomain

## Infra Stuff
- ~~[ ] replace `traefik` with nginx ingress for atom-hive~~

## Podspec stuff
- ~~[ ] add ingress endpoint under earlgreyders.wang for this service~~
- [x] quick and dirty nginx proxy pass to get to the endpoint - using metallb with a static address
- [x] deploying from github registry

## CI/CD Stuff
- [x] github actions? _yup, added container builder and registry stuff_
- [x] gitops deploys _used argocd_
- [ ] argo could benefit from PV/PVC, might be worth moving to hive
- [ ] update argo for `aiotest` so it's smooth with merged to `main`
