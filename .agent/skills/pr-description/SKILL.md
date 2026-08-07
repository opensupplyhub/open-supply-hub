---
name: pr-description
description: Write high-quality pull request descriptions using the repository's pull_request_template.md and Google's CL description best practices. Use when creating a pull request, writing a PR description, or when the user asks to describe changes for a PR or merge request.
---

# Writing Good PR Descriptions

Based on [Google's CL description guidelines](https://google.github.io/eng-practices/review/developer/cl-descriptions.html).

A PR description is a public record of change. It must communicate:

1. **What** change is being made — summarize so readers understand without reading the entire diff.
2. **Why** these changes are being made — what context did the author have? What decisions aren't reflected in the code?

The description becomes a permanent part of version control history. Future developers will search for the PR based on its description. If all the important information is in the code and not the description, it will be much harder to locate. And even after finding it, they need to understand _why_ the change was made — code reveals what the software does, but not why it exists.

IMPORTANT: THE DESCRIPTION SHOULD BE EASY TO READ AND CONCISE!!!

## Required Structure

IMPORTANT: The PR body MUST follow the repository template at [`pull_request_template.md`](../../../pull_request_template.md) (repo root). Read that file first — it is the single source of truth. If it has changed, follow the file, not the outline below.

Reproduce every section, in order, with the guidance HTML comments stripped out:

```markdown
## Jira Ticket

[OSDEV-123](https://opensupplyhub.atlassian.net/browse/OSDEV-123)

---

## Summary of Changes

<the what/why writing described in the rest of this skill>

---

## Type of Change

- [x] <only the boxes that apply>

---

## Testing

<how the change was verified>

---

## Known TODO Items

<deferred work, follow-up tickets, known limitations — or "None">

---

## Checklist

### Implementation
### Testing & Validation
### Documentation & Communication
### Final Review
```

Rules:

- **Do not** invent, drop, rename, or reorder sections, and keep the `---` separators.
- Replace each `N/A` placeholder with real content. Leave `N/A` only when the section genuinely does not apply, and explain why in **Summary of Changes**.
- **Jira Ticket**: derive the ticket id from the branch name (see Gathering Context) and link it in the `[OSDEV-123](...)` format. Use `N/A` only for PRs with no ticket.
- **Type of Change**: check all applicable boxes. This drives what reviewers look at, so be accurate — a UI change needs the UI box, a schema change needs the backend box.
- **Testing**: list the scenarios actually covered (happy path, edge cases, regressions). Attach screenshots or a recording for UI changes; note the requests/queries run for backend changes.
- **Known TODO Items**: write `None` rather than deleting the section.
- **Checklist**: keep all four subsections and every item. Only check a box when the work was genuinely done and verified. Never check boxes on the author's behalf by assumption — leave them unchecked and tell the user which ones need their attention. Uncheck (or annotate) items that don't apply.

Everything below applies to the **PR title** and the **Summary of Changes** section.

## Gathering Context

Before writing the description, run these commands in parallel to understand the full scope of changes:

- `git log --oneline <base-branch>..HEAD`
- `git diff <base-branch>..HEAD --stat`
- `git diff <base-branch>..HEAD`
- `git log <base-branch>..HEAD --format="%B---"`

Get the ticket id from the current branch name. For example, if the branch name is `OSDEV-1234-add-new-feature`, the ticket id is `OSDEV-1234`. Use the following command to get the ticket id:

```bash
git branch --show-current | grep -oE 'OSDEV-[0-9]+'
```

And then fetch the ticket details from JIRA using the ticket id to get additional context.

## First Line

This is the PR title, and it doubles as the opening line of **Summary of Changes**.

- Short summary of specifically **what** is being done.
- Complete sentence, written as though it were an order (imperative mood).
- Followed by an empty line.

The first line appears in version control history summaries, so it must be informative enough that future code searchers don't have to read the full description to understand what the PR did. It should stand alone, allowing readers to skim history quickly.

Keep it short, focused, and to the point. Clarity and utility to the reader is the top concern.

Say "**Delete** the FizzBuzz RPC and **replace** it with the new system." instead of "**Deleting** the FizzBuzz RPC and **replacing** it with the new system."

The rest of the description does not need to be imperative.

## Body is Informative

This is the rest of **Summary of Changes**. The remaining template sections (Testing, Known TODO Items, Checklist) cover their own ground — don't duplicate them here.

The rest of the description should fill in the details and include any supplemental information a reader needs to understand the changelist holistically:

- A brief description of the problem being solved
- Why this is the best approach
- Any shortcomings to the approach
- Background information: bug/ticket numbers, benchmark results, links to design documents

If you include links to external resources, consider that they may not be visible to future readers due to access restrictions or retention policies. Where possible, include enough context for reviewers and future readers to understand the PR without following the links.

Even small PRs deserve attention to detail. Put the PR in context.

## Bad PR Descriptions

"Fix bug" is an inadequate description. What bug? What did you do to fix it? Other bad examples:

- "Fix build."
- "Add patch."
- "Moving code from A to B."
- "Phase 1."
- "Add convenience functions."
- "kill weird URLs."

These do not provide enough useful information.

## Good PR Descriptions

### Functionality change

> RPC: Remove size limit on RPC server message freelist.
>
> Servers like FizzBuzz have very large messages and would benefit from reuse. Make the freelist larger, and add a goroutine that frees the freelist entries slowly over time, so that idle servers eventually release all freelist entries.

The first few words describe what the PR does. The rest talks about the problem being solved, why this is a good solution, and the specific implementation.

### Refactoring

> Construct a Task with a TimeKeeper to use its TimeStr and Now methods.
>
> Add a Now method to Task, so the borglet() getter method can be removed (which was only used by OOMCandidate to call borglet's Now method). This replaces the methods on Borglet that delegate to a TimeKeeper.
>
> Allowing Tasks to supply Now is a step toward eliminating the dependency on Borglet. Eventually, collaborators that depend on getting Now from the Task should be changed to use a TimeKeeper directly, but this has been an accommodation to refactoring in small steps.
>
> Continuing the long-range goal of refactoring the Borglet Hierarchy.

The first line describes what the PR does and how this is a change from the past. The rest describes the specific implementation, the context, that the solution isn't ideal, and possible future direction. It explains _why_ the change is being made.

### Small PR that needs some context

> Create a Python3 build rule for status.py.
>
> This allows consumers who are already using this as in Python3 to depend on a rule that is next to the original status build rule instead of somewhere in their own tree. It encourages new consumers to use Python3 if they can, instead of Python2, and significantly simplifies some automated build file refactoring tools being worked on currently.

The first sentence describes what's being done. The rest explains _why_ and gives the reviewer context.

## Using Tags

Tags are manually entered labels that categorize PRs (e.g. `[tag]`, `#tag`, `tag:`). They are optional.

If using tags, consider whether they belong in the body or the first line. Limit tag usage in the first line so it doesn't obscure the content.

Good:

- `[banana] Peel the banana before eating.`
- `#banana #apple: Assemble a fruit basket.`

Bad:

- `[banana peeler factory factory][apple picking service] Assemble a fruit basket.` — too many/long tags overwhelm the first line.

## Review Before Submitting

PRs can undergo significant change during review. Review the description before submitting to ensure it still reflects what the PR does.

Before opening or updating the PR, confirm:

- [ ] Every section of `pull_request_template.md` is present, in order, with the HTML comments removed.
- [ ] No leftover `N/A` placeholders except where the section truly does not apply.
- [ ] The Jira link resolves and matches the branch's ticket.
- [ ] Type of Change reflects what the diff actually touches.
- [ ] Checked checklist items are all genuinely true; unverified ones are left unchecked and raised with the user.
- [ ] `doc/release/RELEASE-NOTES.md` has been updated on this branch (see AGENTS.md) — if not, prompt the user before opening the PR.
