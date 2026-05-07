# Expert Growth Loop

Weekly loop to improve agent quality safely.

## Step 1: Benchmark

- Run one coding task, one bugfix task, one release task.
- Capture outputs from `scripts/report.py weekly` and `scripts/cost_report.py weekly`.

## Step 2: Diagnose

- Identify top 3 failure or friction patterns.
- Map each pattern to exactly one root cause:
  - prompt gap
  - template gap
  - workflow gap
  - tool/permission gap

## Step 3: Improve

- Implement 1-2 focused improvements only.
- Update role docs / skills / policies accordingly.

## Step 4: Validate

- Re-run at least one real task.
- Compare before/after on quality, speed, and cost.

## Step 5: Decide

- Keep change if metrics improved or stayed equal with lower cost.
- Revert change if quality regresses.

Human orchestrator approval is mandatory at Step 5.

