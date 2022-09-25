# TODO List

## Code
- [x] Selenium 4 `DeprecationWarning: executable_path has been deprecated, please pass in a Service object` _fixed?_
- [x] Selenium 4 `DeprecationWarning: service_log_path has been deprecated, please pass in a Service object`
(This one is tough- while they claim to have deprecated `service_log_path`, for geckodriver there isn't a native flag that I see)
- [x] Add some args support (quiet)
- [x] output in json

## Container Stuff
- [x] Create Container that can run selenium based on https://github.com/m9brady/triumph-tracker
- [ ] selenium job as cron/timed event
- [ ] display pretty page with stats from selenium job
- [ ] Store container in github registry
- [ ] stretch: discord shit?

## Infra Stuff
- [ ] replace `traefik` with nginx ingress for atom-hive

## Podspec stuff
- [ ] add ingress endpoint under earlgreyders.wang for this service

## CI/CD Stuff
- [ ] github actions?
- [ ] gitops deploys, argo? cron?
