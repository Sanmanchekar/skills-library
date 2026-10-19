# Contract Testing Skill — Pact Consumer-Driven Contracts & can-i-deploy for Claude Code, Cursor, Copilot

> **Stop breaking consumers when the API changes.** Consumer-driven contract tests with Pact (or Spring Cloud Contract / OpenAPI schemas), provider states, a broker, and a can-i-deploy gate — for HTTP and async messages.

**Keywords**: contract testing, consumer driven contracts, pact testing, pact broker, pactflow, can-i-deploy, provider verification, provider states, spring cloud contract, async message contracts, kafka contract test, microservice integration testing, contract testing claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- contract-testing
```

## What it does

- Chooses the approach — **Pact**, **Spring Cloud Contract**, or **schema-based** (OpenAPI / AsyncAPI / Protobuf breaking-change diffs)
- Reads the consumer code to contract **only the fields it actually reads**
- Writes consumer tests with **type/regex matchers**, not brittle literals
- Defines **provider states** and the state handlers that seed data
- Wires the **Pact Broker**, pending/WIP pacts, **can-i-deploy**, and record-deployment into CI
- Covers **async message contracts** for Kafka / SQS / RabbitMQ events
- Lists **what NOT to put in a contract** — business rules, exact values, auth tokens, SLAs

## When it triggers

- "Add contract tests between X and Y" / "set up Pact"
- "Consumer-driven contracts" / "can-i-deploy"
- "Our API changes keep breaking the frontend"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [e2e-testing](../e2e-testing) — fewer, slower tests once contracts cover integration
- [test-generation](../test-generation) — unit tests for provider business logic
- [api-design-python-fastapi](../api-design-python-fastapi) — design the API the contract pins
- [deploy-plan](../deploy-plan) — can-i-deploy as a promotion gate
