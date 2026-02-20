# Using /create-meta-prompt in Claude Code: Team Guide

This guide shows your team how to leverage the `/create-meta-prompt` command in Claude Code to build structured, multi-stage workflows.

## Why This Matters

Instead of ad-hoc prompting and hoping for good outputs, `/create-meta-prompt` provides a **structured system** for:

- Creating prompts that other Claude instances can execute reliably
- Building multi-stage workflows (research &rarr; plan &rarr; implement)
- Automatically detecting and tracking dependencies between tasks
- Generating SUMMARY.md files so humans can scan results quickly
- Running independent prompts in parallel for faster throughput

## Quick Start: How to Invoke

In your terminal with Claude Code running, type:

```
/create-meta-prompt [your task]
```

For example:

```
/create-meta-prompt research authentication strategies for our API
```

Claude will:
1. Determine the task type (Do, Plan, Research, or Refine)
2. Ask targeted clarifying questions via interactive prompts
3. Generate an optimized, XML-structured prompt
4. Save it to `.prompts/` with numbered sequencing
5. Present a decision tree: **Run now**, **Review first**, or **Save for later**

## The Four Task Types

Know which one you need&mdash;Claude will detect it from keywords, but being explicit helps:

### **Do** &ndash; Execute a Task, Produce an Artifact
When you need to **build, fix, refactor, or create something**.

Examples:
- "Implement user authentication"
- "Fix the checkout bug"
- "Refactor the database layer"
- "Add email notifications"

**Output**: Code, files, or implementation artifacts saved in your project.

### **Plan** &ndash; Create an Approach or Strategy
When you need to **decide how to do something before building it**.

Examples:
- "Plan how we should handle payments"
- "Create a migration strategy for our database schema"
- "Design the architecture for real-time notifications"

**Output**: Structured strategy document in `.prompts/` with phases, decisions, tradeoffs, and implementation order.

### **Research** &ndash; Gather Information or Understand Something
When you need to **explore options, understand requirements, or evaluate approaches**.

Examples:
- "Research authentication methods suited for our API"
- "Investigate performance issues in the dashboard"
- "Explore open-source libraries for data visualization"

**Output**: Analysis document in `.prompts/` with findings, confidence levels, quality reports, and open questions.

### **Refine** &ndash; Improve an Existing Research or Plan Output
When you want to **iterate on something you've already created**.

Examples:
- "Improve the authentication plan with more security considerations"
- "Expand the research with newer technologies"

**Output**: Updated document with version tracking, preserving previous iterations in an `archive/` folder.

## Folder Structure: Understanding the Organization

When you create and run prompts, Claude organizes them like this:

```
.prompts/
├── 001-auth-research/
│   ├── completed/
│   │   └── 001-auth-research.md      # Original prompt (archived after run)
│   ├── auth-research.md              # Full output (XML structured for Claude)
│   └── SUMMARY.md                    # Executive summary (human-readable)
├── 002-auth-plan/
│   ├── completed/
│   │   └── 002-auth-plan.md
│   ├── auth-plan.md
│   └── SUMMARY.md
├── 003-auth-implement/
│   ├── completed/
│   │   └── 003-auth-implement.md
│   └── SUMMARY.md                    # Do prompts create code elsewhere
├── 004-auth-research-refine/
│   ├── completed/
│   │   └── 004-auth-research-refine.md
│   └── archive/
│       └── auth-research-v1.md       # Previous version preserved
```

**Key points:**
- Each numbered folder is ONE prompt execution
- `completed/` archives the original prompt after it runs
- Full output goes in the `.md` file (XML-structured for Claude-to-Claude reading)
- `SUMMARY.md` is for humans&mdash;scan this instead of the full output
- Numbers auto-increment, so you don't manage versioning
- Refine tasks preserve previous versions in `archive/`

## The SUMMARY.md Advantage

Every prompt output includes a `SUMMARY.md` with:

```markdown
## Summary: Authentication Research (v1)

**One-liner**: Evaluated JWT, session-based, and OAuth approaches for API security.

**Key Findings**:
- JWT recommended for stateless APIs (our use case)
- Session-based better for traditional web apps
- OAuth needed only if supporting third-party integrations

**Decisions Needed**:
- Confirm token expiration time (15 min or 1 hour?)
- Decide if we need refresh tokens

**Blockers**:
- Need security review from team

**Next Step**:
Proceed to 002-auth-plan to design implementation strategy
```

**Why this matters**: Your team doesn't have to read 2000-word analysis documents. Scan the SUMMARY, then dive into the full output only if needed.

## Common Workflows

### Workflow 1: Single Task (Do)
**Goal**: Implement a feature

```
1. In Claude Code, run:
   /create-meta-prompt implement user password reset flow

2. Claude asks clarifying questions via interactive prompts
   → You answer inline

3. Claude creates: .prompts/001-password-reset-implement/

4. Claude presents the decision tree:
   → Select "Run now"

5. Claude launches a Task agent to execute the prompt

6. Prompt executes and creates code + SUMMARY.md

Result: Password reset feature is implemented.
```

### Workflow 2: Multi-Stage (Research &rarr; Plan &rarr; Implement)
**Goal**: Build a complex feature with proper planning

```
Stage 1 - Research:
/create-meta-prompt research payment processing options
→ Creates: .prompts/001-payments-research/
→ Run it. SUMMARY.md shows options, tradeoffs, recommendation

Stage 2 - Plan (auto-detects Stage 1):
/create-meta-prompt plan our payment implementation
→ Claude detects existing payment research via dependency scanning
→ Automatically references 001-payments-research output
→ Creates: .prompts/002-payments-plan/
→ Output: Architecture, implementation steps, decision points

Stage 3 - Implement (auto-detects Stage 2):
/create-meta-prompt implement payments based on the plan
→ Claude detects existing payment plan
→ Automatically references 002-payments-plan output
→ Creates: .prompts/003-payments-implement/
→ Output: Code, integrated into your project
```

**Dependency Detection**: Claude automatically scans for `@.prompts/` references and existing outputs to build the dependency graph. No manual wiring needed.

### Workflow 3: Iterate on Research
**Goal**: Deepen analysis with more options

```
After 001-auth-research completes:
/create-meta-prompt refine the authentication research
→ Claude detects auth-research.md as the target
→ Creates: .prompts/002-auth-research-refine/
→ Archives previous version to archive/auth-research-v1.md
→ New version includes deeper analysis

Result: Better research without losing the original version.
```

### Workflow 4: Parallel Execution
**Goal**: Run independent research tasks simultaneously

```
/create-meta-prompt research frontend frameworks AND research backend APIs

→ Claude detects these are independent tasks
→ Creates both prompts
→ Launches Task agents in parallel
→ Both complete independently, results collected

Result: Two research outputs ready at the same time.
```

## How Dependency Detection Works

Claude Code's `/create-meta-prompt` includes an intelligent dependency engine:

1. **Automatic scanning**: Looks for `@.prompts/{number}-{topic}/` references in prompt content
2. **Topic inference**: When no explicit references exist, detects related outputs by matching topic names
3. **Graph construction**: Builds a dependency DAG (directed acyclic graph) and detects cycles
4. **Execution ordering**: Determines whether to run sequentially, in parallel, or in mixed mode

You don't need to manually wire dependencies. Claude handles it.

## Structured Metadata (Claude-to-Claude)

Research and Plan outputs include XML metadata that downstream prompts can consume:

```xml
<metadata>
  <confidence level="high">
    Based on official documentation and tested examples
  </confidence>
  <dependencies>
    Requires Node.js 18+, Stripe SDK v12
  </dependencies>
  <open_questions>
    Webhook retry policy not confirmed
  </open_questions>
  <assumptions>
    Using PostgreSQL as primary database
  </assumptions>
</metadata>
```

This structured format ensures that when a Plan prompt consumes Research output, or an Implement prompt consumes Plan output, the consuming prompt has machine-readable context about confidence and gaps.

## Key Advantages Over Manual Prompting

| Manual Prompting | Using /create-meta-prompt |
|---|---|
| "Build auth system" &rarr; vague results | Structured intake questions &rarr; precise output |
| Multiple chat sessions scattered around | All organized in `.prompts/` with numbering |
| No way to chain research&rarr;plan&rarr;build | Auto-detects dependencies and references |
| Have to read full 3000-word outputs | SUMMARY.md lets you scan in 30 seconds |
| Restarting? Redo from scratch | Saved prompts can be re-run, refined, iterated |
| Hard to share outputs with team | `.prompts/` is version-controlled, easy to review |
| Sequential execution only | Parallel execution for independent tasks |
| No quality validation | Post-execution validation checks outputs |

## Execution Modes

Claude Code supports three execution strategies:

- **Single**: One prompt, straightforward run via a Task agent
- **Sequential**: Multiple prompts where each depends on the previous output&mdash;runs in order
- **Parallel**: Independent prompts launched as concurrent Task agents in a single message
- **Mixed**: Complex DAGs with some parallel branches and some sequential chains

Claude determines the mode automatically based on the dependency graph.

## Team Distribution Tips

1. **Commit `.prompts/` folder to git**
   - Makes outputs visible to the team
   - Preserves chain history
   - SUMMARY.md files are great for PRs: "Here's what we researched"

2. **Use SUMMARY.md in documentation**
   - Link to SUMMARY.md when explaining decisions
   - Keeps docs fresh from actual analysis

3. **Establish a naming convention**
   - Topic names: `auth`, `payments`, `dashboard`, `notifications`
   - Makes it easy to spot related work and helps dependency detection

4. **Refine instead of recreating**
   - Instead of "Create new research," use Refine
   - Preserves iteration history with archived versions

## Example: Real Workflow

Your team needs to add Stripe integration:

**Step 1 - Research**
```
/create-meta-prompt research Stripe integration options for our subscription model
```
&rarr; Creates: `.prompts/001-stripe-research/`
&rarr; SUMMARY tells you: JWT for tokens, webhooks for events, test mode for development

**Step 2 - Plan**
```
/create-meta-prompt plan our Stripe integration
```
&rarr; Auto-references: `001-stripe-research/`
&rarr; Creates: `.prompts/002-stripe-plan/`
&rarr; SUMMARY shows: Database schema, API endpoints, webhook handling, security checklist

**Step 3 - Implement**
```
/create-meta-prompt implement Stripe based on the plan
```
&rarr; Auto-references: `002-stripe-plan/`
&rarr; Creates: `.prompts/003-stripe-implement/`
&rarr; SUMMARY shows: Files created, tests written, deployment notes

**Step 4 - Code Review**
```
Push to GitHub. Reviewer checks:
- .prompts/003-stripe-implement/SUMMARY.md (what was built)
- Implementation code (generated from plan)
- Tests (included in implementation)
```

## Troubleshooting

**Q: "Claude asks too many questions"**
A: Provide more context upfront. Instead of `/create-meta-prompt build a dashboard`, say `/create-meta-prompt build an admin dashboard for user management in React with TypeScript`. Fewer questions needed.

**Q: "I want to change the prompt after it's created"**
A: Edit the `.md` file in `.prompts/[number]-[name]/completed/` before running, OR create a Refine prompt to iterate.

**Q: "How do I know what to run first in multi-stage workflows?"**
A: Claude auto-detects dependencies and determines execution order. Check the SUMMARY.md files&mdash;they show "Next Step: Run prompt X."

**Q: "Can I run multiple prompts in parallel?"**
A: Yes. If the prompts don't depend on each other's outputs, Claude launches them as concurrent Task agents. Independent tasks execute simultaneously.

**Q: "Can I re-run a completed prompt?"**
A: Move the prompt file from `completed/` back to the parent folder and ask Claude to run it again.

## Getting Started This Week

1. **Pick a task** you're working on
2. **Determine the type**: Do, Plan, Research, or Refine
3. **Open Claude Code** in your terminal
4. **Run**: `/create-meta-prompt [task type] [what you need]`
5. **Answer Claude's questions**&mdash;provide what you know, Claude fills gaps
6. **Choose from the decision tree**&mdash;Run now, Review first, or Save for later
7. **Check `.prompts/` folder**&mdash;see your organized output with SUMMARY.md

## Questions?

If your org uses this widely, bookmark this guide and share it when onboarding new team members.
