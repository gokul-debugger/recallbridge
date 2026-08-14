# Contributing To RecallBridge

Thank you for helping make public recall information easier to use.

## Before You Start

1. Search existing issues and pull requests.
2. Open or claim an issue before making a substantial change.
3. Keep safety claims conservative and preserve links to official records.
4. Do not commit API responses containing private data, generated databases, or secrets.

Good first contributions include source fixtures, accessibility improvements, connector contract tests, documentation corrections, and small watchlist improvements.

## Development

Follow the setup instructions in the README. Before opening a pull request, run:

```bash
npm run lint
npm run test
npm run build
pytest -q
ruff check backend scripts
npm run test:e2e
```

Use small, focused commits. Add or update tests for behavioral changes.

## Source Connector Requirements

New connectors must:

- use an official public source;
- preserve the source record ID and URL;
- normalize dates, identifiers, status, hazard, and remedy without inventing data;
- include representative response fixtures and tests;
- fail independently so one unavailable source does not block other sources; and
- document geographic coverage and source limitations.

## Pull Requests

Describe the user problem, the chosen solution, and the checks you ran. Include screenshots for visible changes. A maintainer may ask for revisions before merge.
