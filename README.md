# open-fsm — a generic finite state machine for Python

[![PyPI](https://img.shields.io/pypi/v/open-fsm)](https://pypi.org/project/open-fsm/)
[![Python](https://img.shields.io/pypi/pyversions/open-fsm)](https://pypi.org/project/open-fsm/)
[![License](https://img.shields.io/pypi/l/open-fsm)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-open--byte.github.io-blue)](https://open-byte.github.io/open-fsm/)

A lightweight, **ORM-agnostic finite state machine for Python** — the declarative
decorator API popularised by [`django-fsm`](https://pypi.org/project/django-fsm/),
rebuilt as a standalone core with **zero dependencies** and no Django requirement.

One machine, two jobs: model the **flow** (what may happen next, and who is allowed
to make it happen) and bind it to **stored state** in whatever persists your objects —
**Django**, **SQLAlchemy**, **Tortoise ORM**, dataclasses, or plain Python objects.

```bash
pip install open-fsm
```

> [!IMPORTANT]
> `open-fsm` starts from the idea behind [`django-fsm`](https://pypi.org/project/django-fsm/): declare the states, decorate the methods that move between them, and let the machine refuse everything else.
>
> Thanks to Mikhail Podgurskiy for writing django-fsm and maintaining it for so many years.
>
> django-fsm lives on Django models — the state is a model field, the transitions are model methods. That is exactly right inside a Django project, and unavailable anywhere else.
>
> `open-fsm` keeps the declarative API and drops the coupling. The machine is a plain Python class, and *where the state is stored* is a separate, pluggable concern: a Django field, a Tortoise or SQLAlchemy column, a dataclass attribute, or nothing at all. Fully typed, zero dependencies.

## Documentation

**[open-byte.github.io/open-fsm](https://open-byte.github.io/open-fsm/)** — guides, reference and a worked tutorial. Every example on the site is executed by the test suite.

| | |
| --- | --- |
| [Getting Started](https://open-byte.github.io/open-fsm/getting-started/) | Build a machine from an empty file |
| [Transitions](https://open-byte.github.io/open-fsm/guides/transitions/) | Sources, targets, wildcards and labels |
| [Conditions](https://open-byte.github.io/open-fsm/guides/conditions/) | Refusals that explain themselves |
| [Dataclasses](https://open-byte.github.io/open-fsm/guides/dataclasses/) | Declaring the field on a generated class |
| [Binding state to storage](https://open-byte.github.io/open-fsm/guides/persistence/) | Keeping the state in a database row |
| [Errors](https://open-byte.github.io/open-fsm/reference/errors/) | Every exception and what triggers it |

Runnable versions of the examples live in [`examples/README.md`](examples/README.md).

## Quick start

Declare a `State` field on any plain class, then mark the methods that move between states:

```python
from enum import Enum

from open_fsm import State, StateEngine


class ReviewState(str, Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class Article(StateEngine):
    state = State(ReviewState, default=ReviewState.DRAFT)

    def __init__(self, title, body=""):
        self.title = title
        self.body = body

    @state.transition(
        source=ReviewState.DRAFT,
        target=ReviewState.IN_REVIEW,
        conditions=[lambda article: bool(article.body)],
    )
    def submit(self):
        ...

    @state.transition(source=ReviewState.IN_REVIEW, target=ReviewState.APPROVED)
    def approve(self):
        ...

    @state.transition(source=ReviewState.IN_REVIEW, target=ReviewState.REJECTED)
    def reject(self):
        ...

    @state.transition(source=ReviewState.APPROVED, target=ReviewState.PUBLISHED)
    def publish(self):
        ...

    @state.transition(source=State.ANY, target=ReviewState.ARCHIVED)
    def archive(self):
        ...
```

Five transitions. `submit`, `approve`, `reject` and `publish` each move between two specific states; `archive` is declared with `State.ANY`, so it is reachable from anywhere.

Calling a transition method runs its body and moves the state:

```python
article = Article("Hello", body="...")
article.state                   # ReviewState.DRAFT

article.submit()
article.approve()
article.publish()
article.state                   # ReviewState.PUBLISHED
```

A transition that does not exist from the current state is refused, and the state is never assignable by hand:

```python
article.publish.can_proceed()   # False
article.publish()               # NoTransition: Publish :: no transition from "PUBLISHED"

article.state = ReviewState.DRAFT
# AttributeError: Direct state modification is not allowed
```

### Asking what is possible

Inheriting `StateEngine` gives every instance three introspection methods:

```python
draft = Article("No body yet")

[t.slug for t in draft.get_outgoing_transitions()]    # ['archive', 'submit']
[t.slug for t in draft.get_available_transitions()]   # ['archive']
```

`submit` leaves `DRAFT`, so it is *outgoing* — but its condition (a non-empty body) is unmet, so it is not *available*. `get_transitions()` returns the whole machine, regardless of the current state.

The same three exist as module-level functions, for classes that cannot inherit the mixin. Those also take a state, so you can ask about one the flow is not in:

```python
from open_fsm import get_outgoing_transitions

[t.slug for t in get_outgoing_transitions(draft, ReviewState.IN_REVIEW)]
# ['approve', 'archive', 'reject']
```

## Features

* ORM-agnostic
* Lightweight and reusable
* Framework-independent core
* A single machine for both flows and persisted models
* Designed to support multiple ORMs
* Fully typed, ships a PEP 561 `py.typed` marker
* A declarative API in the spirit of `django-fsm`, without Django

## ORM Integrations

Binding a machine to stored state works today with `@state.getter()`, `@state.setter()` and `@state.on_success()` — see [Binding state to storage](https://open-byte.github.io/open-fsm/guides/persistence/).

Dedicated wrappers are the next thing to build. Their proposed APIs are written up so the shape can be reviewed before they ship:

* [Django ORM](https://open-byte.github.io/open-fsm/integrations/django/) — planned
* [Tortoise ORM](https://open-byte.github.io/open-fsm/integrations/tortoise/) — planned
* [SQLAlchemy](https://open-byte.github.io/open-fsm/integrations/sqlalchemy/) — planned

## License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for the full license text.

## Attribution

The declarative transition API this package builds on was pioneered by `django-fsm`, written by Mikhail Podgurskiy and released under the MIT License.
