# Multi-Pass Answer Protocol

Goal: improve answer quality by requiring internal multi-round reasoning and tool-backed verification before final output.

## Required Passes

1. Problem Framing Pass
- Clarify objective, constraints, and acceptance criteria.
- Identify unknowns and risk points.

2. Evidence Pass
- Use tools/logs/docs to gather concrete evidence.
- Prefer primary project artifacts over assumptions.

3. Validation Pass
- Cross-check output against acceptance criteria.
- Run at least one verification step (script/test/checklist) when applicable.

4. Finalization Pass
- Produce concise final output with decisions, evidence, and next steps.

## Rules

- Do not output final answer after only one shallow pass.
- Do not skip validation when a tool check is available.
- When uncertainty remains, state residual risk explicitly.

