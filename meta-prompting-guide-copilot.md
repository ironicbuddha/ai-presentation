    # Using create-meta-prompts in Copilot Chat: Team Guide

    This guide shows your team how to leverage the `create-meta-prompts` skill in VS Code Copilot Chat to build structured, multi-stage Claude workflows.

    ## Why This Matters

    Instead of asking vague questions in Copilot Chat and hoping for good outputs, `create-meta-prompts` provides a **structured system** for:

    - ✅ Creating prompts that other Claude instances can execute reliably
    - ✅ Building multi-stage workflows (research → plan → implement)
    - ✅ Automatically tracking dependencies between tasks
    - ✅ Generating SUMMARY.md files so humans can scan results quickly
    - ✅ Creating organized, repeatable processes

    ## Quick Start: How to Invoke

    In VS Code Copilot Chat, just ask:

    ```
    Create a meta-prompt for [your task]
    ```

    Or be more specific:

    ```
    Create a meta-prompt to research authentication strategies for our API
    ```

    Copilot will:
    1. Ask clarifying questions to understand your purpose
    2. Identify the task type (Do, Plan, Research, or Refine)
    3. Generate an optimized prompt
    4. Save it to `.prompts/` folder with numbered sequencing
    5. Show you what to do next

    ## The Four Task Types

    Know which one you need—Copilot will ask, but knowing helps you answer faster:

    ### **Do** - Execute a Task, Produce an Artifact
    When you need to **build, fix, refactor, or create something**.

    Examples:
    - "Implement user authentication"
    - "Fix the checkout bug"
    - "Refactor the database layer"
    - "Add email notifications"

    **Output**: Code, files, or implementation artifacts saved in your project.

    ### **Plan** - Create an Approach or Strategy
    When you need to **decide how to do something before building it**.

    Examples:
    - "Plan how we should handle payments"
    - "Create a migration strategy for our database schema"
    - "Design the architecture for real-time notifications"

    **Output**: Structured strategy document in `.prompts/` with decisions, tradeoffs, and implementation order.

    ### **Research** - Gather Information or Understand Something
    When you need to **explore options, understand requirements, or evaluate approaches**.

    Examples:
    - "Research authentication methods suited for our API"
    - "Investigate performance issues in the dashboard"
    - "Explore open-source libraries for data visualization"

    **Output**: Analysis document in `.prompts/` with findings, confidence levels, and open questions.

    ### **Refine** - Improve an Existing Research or Plan Output
    When you want to **iterate on something you've already created**.

    Examples:
    - "Improve the authentication plan with more security considerations"
    - "Expand the research with newer technologies"

    **Output**: Updated document with versioning, preserving previous iterations.

    ## Folder Structure: Understanding the Organization

    When you create prompts, Copilot organizes them like this:

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
    │   ├── auth-plan.md                  # Full output
    │   └── SUMMARY.md
    ├── 003-auth-implement/
    │   ├── completed/
    │   │   └── 003-auth-implement.md
    │   └── SUMMARY.md                    # Do prompts create code elsewhere
    ```

    **Key points:**
    - Each numbered folder is ONE prompt execution
    - `completed/` folder archives the original prompt after it runs
    - Full output goes in the `.md` file (structured for Claude-to-Claude reading)
    - `SUMMARY.md` is for humans—scan this instead of the full output
    - Numbers auto-increment, so you don't manage versioning

    ## The SUMMARY.md Advantage

    Every prompt output includes a `SUMMARY.md` file with:

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
    1. In Copilot Chat, ask:
    "Create a meta-prompt to implement user password reset flow"

    2. Copilot asks: "What should this include?" → You answer

    3. Copilot creates: .prompts/001-password-reset-implement/

    4. You get prompt created message

    5. Copilot asks: "Run now, review first, or save for later?"
    → Select "Run prompt now"

    6. Prompt executes and creates code + SUMMARY.md

    Result: Password reset feature is implemented.
    ```

    ### Workflow 2: Multi-Stage (Research → Plan → Implement)
    **Goal**: Build a complex feature with proper planning

    ```
    Stage 1 - Research:
    "Create a meta-prompt to research payment processing options"
    → Creates: .prompts/001-payments-research/
    → Output: SUMMARY.md shows options, tradeoffs, recommendation

    Stage 2 - Plan (references Stage 1):
    "Create a meta-prompt to plan our payment implementation"
    → Copilot detects: "Found payment research output. Reference it?"
    → Select: Yes
    → Creates: .prompts/002-payments-plan/
    → Output: Architecture, implementation steps, decision points

    Stage 3 - Implement (references Stage 2):
    "Create a meta-prompt to implement payments based on the plan"
    → Select: Yes, reference the plan
    → Creates: .prompts/003-payments-implement/
    → Output: Code, integrated into your project
    ```

    **Chain Detection Magic**: Copilot sees that stage 2 needs stage 1's output, stage 3 needs stage 2's output. It handles the dependency tracking automatically.

    ### Workflow 3: Iterate on Research
    **Goal**: Deepen analysis with more options

    ```
    After 001-auth-research completes:
    "Create a meta-prompt to refine the authentication research"
    → Copilot asks: "Which output to improve?" → Select: auth-research.md
    → Copilot detects you want to iterate
    → Creates: .prompts/002-auth-research-refine/
    → New version includes previous iteration in archive/

    Result: Better research without losing the original version.
    ```

    ## How to Reference Previous Outputs

    When Copilot detects existing research or plan files, you'll see:

    ```
    Found existing outputs:
    - auth-research.md (in 001-auth-research/)
    - stripe-plan.md (in 005-stripe-plan/)

    Should this prompt reference any of these?
    ☐ auth-research.md
    ☐ stripe-plan.md
    ☐ None
    ```

    **Check the ones you want referenced.**

    Copilot will:
    - Include their contents in the new prompt
    - Set up proper dependencies (execution order)
    - Track the chain for SUMMARY.md files

    ## Key Advantages Over Manual Prompting

    | Manual Prompting | Using create-meta-prompts |
    |---|---|
    | "Build auth system" → vague results | Structured intake questions → precise output |
    | Multiple Copilot chats scattered around | All organized in `.prompts/` with numbering |
    | No way to chain research→plan→build | Auto-detects dependencies and references |
    | Have to read full 3000-word outputs | ✅ SUMMARY.md lets you scan in 30 seconds |
    | Restarting? Redo from scratch | Saved prompts can be run again, refined, iterated |
    | Hard to share outputs with team | `.prompts/` is version-controlled, easy to review |

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
    - Makes it easy to spot related work

    4. **Refine instead of recreating**
    - Instead of "Create new research," use Refine
    - Preserves iteration history

    ## Example: Real Workflow

    Your team needs to add Stripe integration:

    **Step 1 - Research**
    ```
    "Create a meta-prompt to research Stripe integration options 
    for our subscription model"
    ```
    → Creates: `.prompts/001-stripe-research/`
    → SUMMARY tells you: JWT for tokens, webhooks for events, test mode for development

    **Step 2 - Plan**
    ```
    "Create a meta-prompt to plan our Stripe integration"
    ```
    → References: `001-stripe-research/`
    → Creates: `.prompts/002-stripe-plan/`
    → SUMMARY shows: Database schema, API endpoints, webhook handling, security checklist

    **Step 3 - Implement**
    ```
    "Create a meta-prompt to implement Stripe based on the plan"
    ```
    → References: `002-stripe-plan/`
    → Creates: `.prompts/003-stripe-implement/`
    → SUMMARY shows: Files created, tests written, deployment notes

    **Step 4 - Code Review**
    ```
    Push to GitHub. Reviewer checks:
    - .prompts/003-stripe-implement/SUMMARY.md (what was built)
    - Implementation code (generated from plan)
    - Tests (included in implementation)
    ```

    ## Troubleshooting

    **Q: "Copilot asks too many questions"**
    A: Provide more context upfront. Instead of "Build a dashboard," say "Build an admin dashboard for user management in React with TypeScript." Fewer questions needed.

    **Q: "I want to change the prompt after it's created"**
    A: Edit the `.md` file in `.prompts/[number]-[name]/completed/` before running, OR create a Refine prompt to iterate.

    **Q: "How do I know what to run first in multi-stage workflows?"**
    A: Copilot auto-detects dependencies. It'll tell you the order. Check the SUMMARY.md files—they'll show "Next Step: Run prompt X."

    **Q: "Can I run multiple prompts in parallel?"**
    A: If they don't depend on each other's outputs, ask Copilot to run them parallel. Independent tasks can execute simultaneously.

    ## Getting Started This Week

    1. **Pick a task** you're working on
    2. **Determine the type**: Do, Plan, Research, or Refine
    3. **Open VS Code Copilot Chat**
    4. **Ask**: "Create a meta-prompt to [task type] [what you need]"
    5. **Follow Copilot's questions**—answer on what you know, Copilot fills gaps
    6. **Review the generated prompt**—edit if needed
    7. **Run it**—skip to running or save for later
    8. **Check `.prompts/` folder**—see your organized output with SUMMARY.md

    ## Questions?

    If your org uses this widely, bookmark this guide and share it when onboarding new team members.