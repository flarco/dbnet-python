# dbnet

dbnet

# Install
```bash
pip install -U git+git://github.com/flarco/dbnet.git
```

# TODO

## API Endpoints:

**send**: initiated from server to client

**get & others**: initiated from client to server

- X stop-worker
- X get-workers
- send-workers (when changed by server / node)
- X add-worker
- X submit-sql
- X send-query-results (query-data)
- send-query-progress
- X set-state
- send-state (when changed by node)
- set-database
- X get-database
- send-database (when changed by node)
- get-meta-tables
- get-meta-columns
- X set-tab
- X get-tab
- send-tab (when changed by node)
- X get-tasks
- X get-queries
- X search-queries

## Tests

-X Unit tests as SOI Client

- Unit tests as Web Client

## Front-end

### Side menu

- Connections (drop-down) with plus sign to add
  - list databases. Clicking a db activates last query state
- Meta Explorer
- Extract / Load
- Settings

### Activities

- Query
  - Left pane is multi pane
    - Editor
      - Codemirror
    - Schema
    - History
  - A dropdown of sessions (past sessions are analysis sessions) with a plus button
- Meta Explorer
  - allows search accross databases for fields
- Transfer
  - Panes to select type of transfer, source, target, live search box, etc

### Top nav

- Logo brand (centered)
- Right side (socket status, CPU, RAM, processes count)

### Tabs

- META (Permanent)

## Shortcut Keys

### Editor

- F4 is to open schema tab
- F9 is execute SQL block
- F10 is to queue SQL block

## Features

- Ability to favorite a SQL snippet with a name, searchable
