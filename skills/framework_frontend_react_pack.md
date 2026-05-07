# Framework Pack: Frontend React

## Use Cases

- Feature pages and stateful components
- Data fetching and mutation flows
- Form handling and validation

## Design Heuristics

1. Keep components focused and composable.
2. Separate presentational and data-fetching concerns.
3. Co-locate tests with feature modules.
4. Prefer explicit loading/error/empty states.

## Common Pitfalls

- Side-effect loops caused by unstable dependency arrays
- Unbounded re-rendering due to non-memoized handlers
- Inconsistent API error handling across pages

## Test Strategy

- Component behavior tests for user interactions
- API state tests for loading/error paths
- Snapshot use only for stable visual primitives

