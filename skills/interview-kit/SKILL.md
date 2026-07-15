---
name: interview-kit
description: Generate a role-scoped technical interview kit — question set with working reference code, evaluation rubric, and difficulty progression. Covers coding rounds, system design, and take-home. Stack-agnostic; produces role-appropriate content (backend, frontend, SRE, data eng, ML eng, EM). Triggered when the user asks to "prepare an interview", "generate interview questions", "build a take-home", or "help me interview for X role".
---

# interview-kit

## When to use

- User asks: "prepare an interview for X role", "generate interview questions", "build a take-home", "system design questions for Y level"
- Hiring loop planning
- Prepping to interview for a role (candidate side)

## Steps

1. **Clarify inputs** (interview mode — ask BEFORE generating):
   - Role: backend / frontend / full-stack / SRE / data eng / ML eng / EM
   - Level: junior (0-2y) / mid (2-5y) / senior (5-10y) / staff+ (10y+)
   - Stack: language / framework / cloud
   - Round type: 45-min coding · 60-min system design · take-home · pair-programming
   - Signals you want (correctness / debugging / architecture / trade-off reasoning / testing / code quality / velocity)

2. **Pick difficulty per round type**:

   | Round | Junior | Mid | Senior | Staff+ |
   |---|---|---|---|---|
   | Coding | data-structure use, single-file | with tests, mild edge cases | production-quality, error paths | ambiguous spec, requires clarification |
   | System design | components of a small feature | one service, standard APIs | multi-service, DB choice, caching, scaling | company-scale, trade-offs, prior art, unknown unknowns |
   | Take-home | 2-4 hours, one feature | 4-6 hours, feature + tests | 6-8 hours, small system, ops considerations | not usually appropriate |

3. **Produce each question with a working reference solution + rubric.** Never ship a question you haven't solved yourself.

## Round templates

### Coding round (45-60 min)

```markdown
## Question — <one-line description>

### Context (2 min read)
Small realistic scenario. NOT a puzzle. NOT a trick.

### Task
Concrete deliverable. What does "done" look like?

### Constraints
- Time budget
- What they can google (docs yes / snippets no)
- Testing expectations

### Reference solution
` ` `<lang>
<complete working code, ~30-80 lines>
` ` `

### Rubric
| Signal | Weight | What "meets" looks like |
|---|---|---|
| Correctness | 40% | Passes the given examples + at least one edge case they surfaced themselves |
| Approach | 20% | Chose a reasonable data structure; explained trade-offs |
| Code quality | 15% | Named things clearly; broke into small functions; handled errors |
| Communication | 15% | Talked through their thinking; responded to hints without shutting down |
| Testing | 10% | Wrote at least one test; discussed what else they'd test |

### Follow-ups (if time)
- "What if the input is 100M items?"
- "How would you make this concurrent?"
```

### System design round (60 min)

```markdown
## Question — Design <system>

### Prompt (deliberately underspecified)
"Design X. You have 60 minutes."

### Expected clarifying questions (candidate should ask most of these)
- Scale: users, QPS, data volume
- Latency SLA
- Consistency requirements
- Read/write ratio
- Multi-region?

### Reference architecture (staff-level target)
- API layer: ...
- Data model: ...
- Storage: ... (why this DB, what constraint)
- Caching: ... (what layer, invalidation strategy)
- Async: ... (queue, streaming)
- Failure modes: ...
- Trade-offs the candidate SHOULD raise

### Rubric
| Signal | Junior | Mid | Senior | Staff+ |
|---|---|---|---|---|
| Clarifying questions | ~2 | ~4 | ~6, unprompted | drives the scope |
| Component decomposition | prompted | with hints | independently | with alternatives |
| Data model | basic | reasonable | scales, handles edges | trade-offs named |
| Failure modes | prompted | 1-2 | 3-4, actionable | anticipates + mitigates |
| Trade-off articulation | limited | balanced | strong | teaches the interviewer something |
```

### Take-home

```markdown
## Take-home — <feature>

### Time budget
6 hours max (respect their time; anything longer is exploitation)

### Deliverable
Working code + README + tests. Submitted as a GitHub repo or zip.

### Prompt
Concrete, realistic. Should mirror actual work.

### Reference solution
Kept in a private repo. Do NOT share.

### Rubric
| Signal | Weight | What "meets" looks like |
|---|---|---|
| Meets the spec | 30% | Feature works for the given cases |
| Code quality | 25% | Naming, structure, no obvious smells |
| Tests | 20% | Meaningful tests, not just green-check ones |
| README + how-to-run | 15% | Reviewer can run it in 5 min without you |
| Judgement | 10% | Made explicit what they'd do with more time |

### Follow-up interview (30 min)
- Walk through the code together
- "Why this data structure?" / "How would you handle 10x scale?" / "What would you change?"
```

## Question quality checklist

- [ ] Realistic — mirrors actual work at your company
- [ ] Not a puzzle — no "aha" trick
- [ ] Unambiguous when needed, ambiguous where you're testing clarification skill
- [ ] Reference solution exists and works
- [ ] Rubric distinguishes signals, not just "did they finish"
- [ ] Time budget matches difficulty
- [ ] No content that's discoverable on LeetCode (unless deliberate)

## Rules

- NEVER ship a question without solving it yourself
- NEVER use LeetCode hard problems for anything except sanity-checking DSA fundamentals
- NEVER hand a candidate an ambiguous prompt without a rubric for the clarifying-questions signal
- NEVER give take-homes longer than 6 hours — it filters for who has 6 hours to spare, not for talent
- ALWAYS provide a rubric — without one, hiring becomes vibes-based
- ALWAYS calibrate difficulty to level — the SAME question with a HIGHER rubric bar is often better than a harder question
