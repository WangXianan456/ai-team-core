# Budget Control

## Limits

- Monthly cap:
- Weekly cap:
- Daily cap:

## Tiering Strategy

1. Low-cost models for drafting/summarization.
2. Mid/high-cost models for architecture, hard bugs, and final reviews.

## Auto Downgrade Policy

1. At 80% daily budget: stop long-context tasks.
2. At 100% daily budget: only `P0` tasks continue on low-cost tier.

## Weekly Review Inputs

- High-cost call count
- Cost per completed task
- Rework rate after QA

