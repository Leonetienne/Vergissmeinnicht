# Introduction

## Purpose

This requirements database specifies the behaviour of Vergissmeinnicht, a small
self-hosted to-do web application. It is the reference for developers, testers and
anyone changing the system.

## Product overview

Vergissmeinnicht keeps tasks on boards. A new board is a plain task list: type a
task, press Enter, tick it off when done. Lists appear only when a user creates
one, turning the board into a Kanban-like set of columns. Tasks carry an optional
due date, colour and note; due tasks trigger optional email reminders. Done tasks
can be archived and restored. Boards can be shared with other users of the same
instance as observer or editor. Everything the UI does is also available through a
REST API and an MCP server, built on one shared operation layer.

The system runs as a Django application in Docker behind a TLS-terminating reverse
proxy, backed by MariaDB. It is configured through environment variables and
administered through management commands.

## User classes

| Class | Description |
|---|---|
| Visitor | Not logged in. Sees only login and, when enabled, registration. |
| User | A registered user of the web app. |
| Board owner | The user who created a given board. |
| Editor | A user a board is shared with in read and write mode. |
| Observer | A user a board is shared with in read-only mode. |
| API client | A script authenticating with a user's API key. |
| MCP agent | An AI agent authenticating with a user's MCP key. |
| Instance admin | Operates the deployment: environment, cron, management commands. |

## Operating environment

- Docker image from an image registry, running Gunicorn with WhiteNoise; MariaDB.
- A persistent volume at `/app/data` for uploaded backdrops.
- Host cron triggering `send_due_reminders` once a day.
- Optional SMTP server for reminders.
- Current desktop and mobile browsers.

## Out of scope (by design)

- Live synchronisation between users looking at the same board; changes appear on reload.
- Email verification, password reset by email, invitations that need accepting.
- Assigning tasks to users, subtasks, recurring tasks, attachments, comments, tags.
- Server-side change history; undo lives in the browser only.
- Transferring board ownership, public or anonymous boards.
- Languages other than English.
- Enforcing HTTPS inside the application (handled by the reverse proxy).

## Document conventions

See [README.md](README.md) for the item format, EARS templates and tracing.
