---
name: contract-testing
description: Set up consumer-driven contract tests between services — Pact (or Spring Cloud Contract, or schema-based contracts from OpenAPI / AsyncAPI / Protobuf), provider states, a broker with a can-i-deploy gate in CI, contract versioning and branch tagging, async message contracts for queues and event streams, and a list of what must NOT go into a contract. Produces consumer tests, provider verification wiring, and the CI pipeline steps. Triggered when the user says "add contract tests", "set up Pact", "consumer-driven contracts", "can-i-deploy", "stop breaking the frontend when the API changes", or "test the contract between X and Y".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# contract-testing

## When to use

- User says: "add contract tests", "set up Pact", "consumer-driven contracts", "can-i-deploy", "provider verification"
- Two services deployed independently keep breaking each other on API or event changes
- E2E suites are slow/flaky and mostly exist to catch integration breakage
- NOT for testing business logic of the provider — that belongs in the provider's own unit/integration tests

## Approach decision

| Situation | Approach |
|---|---|
| Consumers known, teams can run tests on both sides | **Consumer-driven (Pact)** — consumer writes expectations, provider verifies |
| JVM/Spring provider owns the contract | **Spring Cloud Contract** — provider-written contracts generate stubs for consumers |
| Public API / many unknown consumers | **Schema-based** — OpenAPI/AsyncAPI/Protobuf as the contract + breaking-change diff (oasdiff, buf breaking) |
| Kafka / SQS / RabbitMQ events | **Pact message contracts** or schema registry with compatibility mode (BACKWARD / FULL) |

## Steps

1. **Map the interactions** — read the consumer's HTTP/gRPC clients and message handlers; list every endpoint/topic it actually uses and every field it actually reads.
2. **Write consumer tests** — one per interaction the consumer relies on, using matchers (type/regex/eachLike), not literal values. The test runs the real consumer client against the Pact mock server.
3. **Name provider states** — each interaction declares the precondition (`"order 42 exists and is PAID"`). States describe data, not implementation.
4. **Publish pacts to a broker** (Pact Broker / PactFlow) tagged with consumer version = git SHA and branch.
5. **Wire provider verification** — provider CI fetches pacts for `mainBranch`, `deployedOrReleased`, and matching feature branches; implements a state-handler per provider state that seeds data via repositories/fixtures (no HTTP calls to itself).
6. **Enable pending + WIP pacts** so a new consumer expectation does not break the provider build until the provider has verified it once.
7. **Gate deploys with can-i-deploy** before every environment deploy, then **record-deployment** after it succeeds.
8. **Add async contracts** for message producers/consumers — the contract is the message body + metadata, verified by calling the provider's message-building function, not the broker.
9. **Version and retire** — delete interactions the consumer no longer uses; the broker drops pacts for versions no longer deployed.

## What NOT to put in a contract

| Don't | Why | Instead |
|---|---|---|
| Fields the consumer never reads | Blocks provider changes for no reason | Only assert on what the consumer uses (Postel's law) |
| Exact values (timestamps, IDs, totals) | Brittle; tests data not shape | Type / regex matchers |
| Business rules ("discount is 10% over $100") | Contract tests are not functional tests | Provider unit tests |
| Every error permutation | Combinatorial explosion | One interaction per error *shape* the consumer handles |
| Auth token values | Secrets + expiry | Provider request filter injects a valid token during verification |
| Performance / SLA | Not a contract-test concern | [load-testing](../load-testing) |

## Example — input → output

Input: "`checkout-web` calls `GET /orders/{id}` on `orders-service` and reads `id`, `status`, `total.amount`, `total.currency`."

```javascript
// checkout-web/test/orders.pact.test.js  (Pact JS, V3+)
const { PactV3, MatchersV3: M } = require('@pact-foundation/pact');
const { getOrder } = require('../src/clients/orders');

const provider = new PactV3({ consumer: 'checkout-web', provider: 'orders-service' });

test('fetches a paid order', () => {
  provider
    .given('order 42 exists and is PAID')
    .uponReceiving('a request for order 42')
    .withRequest({ method: 'GET', path: '/orders/42', headers: { Accept: 'application/json' } })
    .willRespondWith({
      status: 200,
      headers: { 'Content-Type': 'application/json' },
      body: {
        id: M.string('42'),
        status: M.regex('PAID|PENDING|CANCELLED', 'PAID'),
        total: { amount: M.integer(1999), currency: M.regex('^[A-Z]{3}$', 'USD') },
      },
    });

  return provider.executeTest(async (mock) => {
    const order = await getOrder(mock.url, '42');
    expect(order.status).toBe('PAID');
  });
});
```

```bash
# CI gate before deploying checkout-web to production
pact-broker can-i-deploy --pacticipant checkout-web --version "$GIT_SHA" --to-environment production
# after a successful deploy
pact-broker record-deployment --pacticipant checkout-web --version "$GIT_SHA" --environment production
```

## Output format

````markdown
# Contract tests — <consumer> → <provider>

## Interactions
| # | Interaction | Provider state | Fields consumer reads | Type |
|---|---|---|---|---|
| 1 | GET /orders/{id} → 200 | order 42 exists and is PAID | id, status, total.* | HTTP |
| 2 | order.paid event | an order has been paid | orderId, paidAt | message |

## Files
- `<consumer>/test/...pact.test.*` — consumer tests (code block per file)
- `<provider>/test/...verify.*` — provider verification + state handlers

## CI pipeline
| Stage | Consumer pipeline | Provider pipeline |
|---|---|---|
| test | run consumer pact tests | verify pacts (mainBranch + deployedOrReleased + pending/WIP) |
| publish | publish pacts tagged SHA + branch | publish verification results |
| pre-deploy | can-i-deploy --to-environment <env> | can-i-deploy --to-environment <env> |
| post-deploy | record-deployment | record-deployment |

## Excluded from the contract (and why)
- <field / rule> — <reason>
````

## Rules

- NEVER assert on fields the consumer does not read — read the consumer code to find out
- NEVER use exact literal values where a type or regex matcher works
- NEVER let provider state handlers call the provider's own HTTP API — seed data directly
- NEVER deploy either side without a passing `can-i-deploy` for the target environment
- NEVER treat contract tests as a replacement for provider functional tests
- ALWAYS tag pacts with git SHA + branch and record deployments per environment
- ALWAYS enable pending/WIP pacts so new consumer expectations don't block unrelated provider builds
- ALWAYS cover async messages if the services talk via a broker — HTTP-only contracts miss half the coupling

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: verify · **Agent**: `verify`
- **Reads**: `api-contract` (from `.lifecycle/<run>/` when present)
- **Writes**: `tests` → `tests.md`
- **Comes after**: api-contract, complexity-aware-coding, pr-description

This skill works on its own; the hand-offs above are suggestions. If the `lifecycle-router` skill is installed, record the step so the next skill can pick up the output: `route.py run record contract-testing --artifact tests=<path>`. If it is not installed, skip this and just name the next skill to the user.
<!-- lifecycle:end -->
