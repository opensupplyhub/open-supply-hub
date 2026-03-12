---
name: pr-description
description: Write high-quality pull request descriptions based on Google's CL description best practices. Use when creating a pull request, writing a PR description, or when the user asks to describe changes for a PR or merge request.
---

# Writing Good PR Descriptions

Based on [Google's CL description guidelines](https://google.github.io/eng-practices/review/developer/cl-descriptions.html).

A PR description is a public record of change. It must communicate:

1. **What** change is being made — summarize so readers understand without reading the entire diff.
2. **Why** these changes are being made — what context did the author have? What decisions aren't reflected in the code?

The description becomes a permanent part of version control history. Future developers will search for the PR based on its description. If all the important information is in the code and not the description, it will be much harder to locate. And even after finding it, they need to understand *why* the change was made — code reveals what the software does, but not why it exists.

## Gathering Context

Before writing the description, run these commands in parallel to understand the full scope of changes:

- `git log --oneline <base-branch>..HEAD`
- `git diff <base-branch>..HEAD --stat`
- `git diff <base-branch>..HEAD`
- `git log <base-branch>..HEAD --format="%B---"`

## First Line

- Short summary of specifically **what** is being done.
- Complete sentence, written as though it were an order (imperative mood).
- Followed by an empty line.

The first line appears in version control history summaries, so it must be informative enough that future code searchers don't have to read the full description to understand what the PR did. It should stand alone, allowing readers to skim history quickly.

Keep it short, focused, and to the point. Clarity and utility to the reader is the top concern.

Say "**Delete** the FizzBuzz RPC and **replace** it with the new system." instead of "**Deleting** the FizzBuzz RPC and **replacing** it with the new system."

The rest of the description does not need to be imperative.

## Body is Informative

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

The first line describes what the PR does and how this is a change from the past. The rest describes the specific implementation, the context, that the solution isn't ideal, and possible future direction. It explains *why* the change is being made.

### Small PR that needs some context

> Create a Python3 build rule for status.py.
>
> This allows consumers who are already using this as in Python3 to depend on a rule that is next to the original status build rule instead of somewhere in their own tree. It encourages new consumers to use Python3 if they can, instead of Python2, and significantly simplifies some automated build file refactoring tools being worked on currently.

The first sentence describes what's being done. The rest explains *why* and gives the reviewer context.

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
