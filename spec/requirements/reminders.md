# Due Date Reminders

### Optional feature
`req~reminders.optional~1`

While `EMAIL_HOST` is not set, the system shall send no reminders, hide the reminder setting and let `send_due_reminders` exit without action.

Covers:
- `feat~reminders~1`

Tags: Operations

### Daily run
`req~reminders.command~1`

The command `send_due_reminders`, run once a day by cron, shall send all reminders that are due.

Covers:
- `feat~reminders~1`

Tags: Operations

### Due soon reminder
`req~reminders.soon~1`

Where email is configured, when an open task's due date is 3 days or less ahead and its "due soon" reminder has not been sent, the system shall send it.

Covers:
- `feat~reminders~1`

### Due reminder
`req~reminders.due~1`

Where email is configured, when an open task's due date is today or past and its "due" reminder has not been sent, the system shall send it.

Covers:
- `feat~reminders~1`

### Once per stage
`req~reminders.once~1`

The system shall send each reminder stage at most once per task; if both stages are due in the same run, then the system shall send only the "due" reminder and mark both as sent; when the due date changes, the system shall reset both stages.

Covers:
- `feat~reminders~1`

### Recipients
`req~reminders.recipients~1`

The system shall send reminders to the board owner and all editors who have reminders switched on, never to observers.

Covers:
- `feat~reminders~1`

Tags: Privacy

### One mail per run
`req~reminders.digest~1`

The system shall send each recipient at most one email per run, listing all their due tasks with board title, due date and a link to the task anchor.

Covers:
- `feat~reminders~1`
