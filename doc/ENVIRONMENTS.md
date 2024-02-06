# OS Hub environments
| ### | Feature | Dev | Test | Pre-prod (staging) | Staging (sandbox) | Production |
| --- | --- | --- | --- | --- | --- | --- |
| Trigger | Push to feature branch | Merging to ogr/develop | Schedule | Merging to releases/vX.Y | Manual | Manual |
| Branch | OSHUB-\* | ogr/develop | ogr/develop | releases/vX.Y | releases/vX.Y | releases/vX.Y |
| Database | Seeded | Seeded | \- Anonymized copy from production | \- Anonymized copy from production | \- staging-db | \- production-db |
| DB Backup | \- None | \- None | \- None | \- None | \- Create | \- Create |
| DB Migration | \- Reset DB | \- Migrate to the latest(preferable)<br>\- Reset DB | \- Migrate to the latest | \- Migrate to the latest | \- Migrate to the latest | \- Migrate to latest |
| Pre-deploy check | \- Lint<br>\- Unit tests<br>\- Code Coverage<br>\- Jest<br>\- UI tests<br>\- Integration tests | \- Lint<br>\- Unit tests<br>\- Code Coverage<br>\- Jest<br>\- UI tests<br>\- Integration tests | \- Lint<br>\- Unit tests<br>\- Code Coverage<br>\- Jest<br>\- UI tests<br>\- Integration tests | \- Lint<br>\- Unit tests<br>\- Jest<br>\- UI tests<br>\- Code coverage<br>\- Integration tests | \- Lint<br>\- Unit tests<br>\- Jest<br>\- UI tests<br>\- Code coverage<br>\- Integration tests | \- Lint<br>\- Unit tests<br>\- Jest<br>\- UI tests<br>\- Code coverage<br>\- Integration tests |
| Pre-deploy error strategy | \- Raise | \- Raise | \- Raise | \- Raise | \- Raise | \- Raise |
| Deploy | \- None | \- Deploy | \- Deploy | \- Deploy | \- Deploy<br>\- Tag-sandbox | \- Deploy<br>\- Tag-production |
| Post-deploy check | \- None | \- Smoke tests on seeded data<br>\- UI tests | \- Smoke tests<br>\- UI tests<br>\- Performance tests (optionally)<br> | \- Smoke tests<br>\- Regression tests<br>\- UI tests<br>\- Performance Tests | \- Smoke tests<br>\- UI tests<br>\- Performance tests (Questionable) | \- Smoke tests<br>\- UI tests<br>\- Performance tests (Questionable) |
| Post-deploy error strategy | \- None | \- Raise | \- Raise | \- Raise | \- Raise | \- Raise |
| Comments: | This is just for running tests for every change in the GitHub pull request during development. | For developers to quickly test stuff after a merge on a stable and predictable database, etc. | Continuous QA and feature verification on an environment close to production in terms of the amount of data, etc. |
