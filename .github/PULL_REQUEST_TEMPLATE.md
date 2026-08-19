<!--
Thanks for contributing to open-fsm.

Keep the sections that apply and delete the ones that do not. A one-line fix
does not need a filled-in form, but the AI assistance section at the bottom is
never optional.
-->

## What this changes

<!-- What the change does and why it is needed. Link the issue if there is one. -->

## How it was verified

<!-- Anything a reviewer should be able to reproduce. -->

- [ ] `make test` — unit tests and the executed documentation examples
- [ ] `make lint` and `make typecheck`
- [ ] `make docs-build` — required if `docs/`, `examples/` or `mkdocs.yml` changed

## Documentation

<!-- Skip this section if the change touches no documented behaviour. -->

- [ ] New or changed behaviour is documented
- [ ] Every ` ```pycon ` transcript was **run**, and its output pasted rather
      than written by hand — see [How These Docs Are Tested](../docs/project/testing.md)
- [ ] Snippet markers referenced by a guide exist in the `examples/` file that owns them
- [ ] New pages are listed in the `nav` of `mkdocs.yml`

## Compatibility

- [ ] Works on Python 3.10 through 3.15, or the matrix in `test.yml` was updated to match
- [ ] No new runtime dependency was added — `open-fsm` ships with none and that is a stated boundary

## AI assistance

`open-fsm` is developed with AI assistance. That is disclosed rather than
hidden, and it does not transfer responsibility: nothing is merged that a human
has not read.

- [ ] This change was developed with AI assistance
- [ ] I have read the complete diff myself and take responsibility for its
      correctness, and for the right to license it under the MIT License

<!--
Leave the first box unchecked if no AI tool was involved. The second is
required either way — it is the human review, and no reviewer or automated
check substitutes for it.
-->
