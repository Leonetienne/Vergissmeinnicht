# Vergissmeinnicht Requirements Database

This directory is the requirements specification (Lastenheft) for Vergissmeinnicht.
It states how the system shall behave. Code is done when it satisfies the
requirements here, and every later change keeps both in sync.

## Format

| Concern | Standard | What it gives us |
|---|---|---|
| Document structure and attributes | ISO/IEC/IEEE 29148:2018 (SRS) | Introduction, glossary, features, functional requirements, quality requirements, design constraints |
| Requirement wording | EARS (Easy Approach to Requirements Syntax, Mavin et al.) | Five sentence templates that keep every statement testable |
| Markdown item syntax | OpenFastTrack (OFT) | Stable IDs, versioning, `Covers` links, machine-checkable with `oft trace` |

### EARS templates

| Pattern | Template |
|---|---|
| Ubiquitous | The system shall *response*. |
| Event-driven | **When** *trigger*, the system shall *response*. |
| State-driven | **While** *state*, the system shall *response*. |
| Unwanted behaviour | **If** *unwanted condition*, **then** the system shall *response*. |
| Optional feature | **Where** *feature is configured*, the system shall *response*. |

Patterns may be combined ("While ..., when ..., the system shall ...").
"Shall" marks a binding requirement. "Should" is not used.

### Item syntax (OpenFastTrack)

```markdown
### Login rate limit
`req~accounts.login-rate-limit~1`

If 5 failed login attempts ..., then the system shall ...

Rationale:
Why this exists, when it is not obvious.

Covers:
- `feat~accounts~1`

Tags: Security
```

- **ID**: `<type>~<name>~<revision>`. Types: `feat` (system feature, in
  [features.md](features.md)) and `req` (requirement, in `requirements/`).
  Names are dot-separated, lower case, each segment starting with a letter.
- **Revision**: bump it whenever the meaning of a requirement changes. Never reuse
  an ID for a different requirement; delete obsolete items instead.
- **Covers**: every `req` covers exactly one `feat`. Every `feat` declares
  `Needs: req`.
- **Tags** (optional): `Security`, `Privacy`, `UI`, `Performance`, `Operations`.
- **Rationale** only where the reason is not evident from the statement.

### Tracing

```bash
oft trace spec/features.md spec/requirements/
```

## Layout

| File | Content |
|---|---|
| [introduction.md](introduction.md) | Purpose, product overview, user classes, out-of-scope list |
| [glossary.md](glossary.md) | Domain terms |
| [features.md](features.md) | System feature list (`feat` items) |
| [requirements/](requirements/) | Functional requirements, one file per feature area |
| [requirements/quality.md](requirements/quality.md) | Quality (non-functional) requirements |
| [requirements/constraints.md](requirements/constraints.md) | Design constraints for maintainers |

## Rules for maintainers

- A behaviour change updates the affected requirements in the same change, next to
  `AGENTS.md`.
- Write requirements as observable behaviour. Code paths belong in `Comment:` only
  when they help find the implementation.
- No em-dashes or en-dashes in this directory.
