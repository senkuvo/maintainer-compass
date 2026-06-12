# Codex for Open Source Application Draft

Use this as a starting point. Replace personal fields with your real identity, email, and OpenAI organization ID.

## Repository URL

`https://github.com/senkuvo/maintainer-compass`

## Role

Primary maintainer

## Why does this repository qualify? 500 characters max

Maintainer Compass helps open-source maintainers reduce review, release, and security toil by auditing repository readiness locally and producing shareable reports. It targets real maintenance workflows: contribution quality, issue templates, CI, security policy, ownership, dependency updates, release notes, and release automation.

## How will you use API credits? 500 characters max

I would use API credits to add optional Codex-powered maintainer automation: issue and PR triage summaries, release-risk summaries, security-policy suggestions, generated maintainer checklists, and review-load reports. The core CLI will remain useful without API access, with AI features opt-in for public OSS maintainers.

## Anything else? 500 characters max

This is a new project, so its strongest current signal is clear ecosystem relevance rather than adoption. It is public, has CI, a first release path, community-health files, and sample maintainer-readiness reports. My goal is to grow it through real use on small open-source repositories.

## Before Submitting

- Confirm your GitHub profile is public.
- Confirm the repository visibility is public.
- Add your OpenAI organization ID.
- Run `python -m unittest discover -s tests`.
- Add more sample reports after scanning real repositories.
