---
name: explain-code
description: Explain a file, function, system, API, database, lambda, or any piece of OS Hub code or infrastructure in plain English, calibrated to the reader's experience level. Use when the user asks to explain, walk through, break down, or describe how something works.
---

# Explaining OS Hub Code and Systems in Plain English

This skill translates anything technical at OS Hub into language the reader can use — a single file, an API endpoint, a database table, a lambda function, or how a whole system fits together.

## Step 1 — Confirm experience level (one-time per session)

If unknown from earlier in the session, ask:

> Quick question so I pitch this right:
> 1. New to code — plain English with real-world analogies
> 2. Some technical comfort — terms are okay, explain non-obvious ones
> 3. Engineer — full technical depth, no analogies needed
>
> Which fits? (1, 2, or 3)

## Step 2 — Ground the answer in real code

Always read the actual source before explaining. Three cases:

- The user pasted code or named a specific file/function → read it directly.
- The user asked about a system, endpoint, lambda, or concept without pointing at specific code → search the OS Hub repo first to find the real implementation, then read it.
- The request is still vague after you look → ask one clarifying question.

If something touches multiple layers (e.g., a lambda that hits the API and the database), read each layer.

## Step 3 — Answer short, pull in only the sections that fit

Default response is concise — aim for under 200 words. Lead with the takeaway, then offer to go deeper. Use only the sections below that the question actually calls for. Don't inflate.

Available sections:

### Infrastructure
Where this runs and what it's built on (Django service, AWS Lambda, Kafka consumer, RDS table, S3 bucket, etc.). Use when the platform matters for the explanation.

### Big Picture
One or two sentences: what this does and where it lives in OS Hub.

### Main Parts
2-4 bullets describing the major pieces. Use when the thing has internal structure worth walking through.

### Analogy
Real-world comparison that makes the concept stick. Especially valuable for Level 1 readers.

Examples:
- "Think of this like a gatekeeper — it checks credentials before letting requests through"
- "This is the recipe card — it lists ingredients and the order to combine them"
- "Picture a referee at a basketball game — this watches the action and flags anything off"

### How Data Flows
If the thing touches multiple systems, trace one concrete example end-to-end. Otherwise skip.

## Step 4 — Offer where to go next

End with:

> Want me to go deeper on a specific part, trace data through it, or explain a related system?

## Style guide

- Read first, explain second — never explain from a filename or assumption
- Use the actual names from the code — don't paraphrase variables, functions, or components
- Level 1 readers: every technical term gets a plain-English definition the first time it appears
- Level 3 readers: skip analogies entirely, name the patterns directly
- Keep the default answer SHORT — depth comes on follow-up, not by default
- Use ONLY the Step 3 sections that fit. A simple file may only need Big Picture + Analogy. A lambda might need Infrastructure + How Data Flows. Match the question.
- If something is unclear, say so — don't guess

## What this skill does NOT do

- Does not modify code (read-only)
- Does not run or test the code
- Does not evaluate whether code is good or should change
