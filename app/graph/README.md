# Lokaah Single Chat Graph

This module implements the "one chat, many skills" backend.

## Agents

- `supervisor` (Nirmola): routes intent
- `veda`: concept teaching
- `oracle`: practice questions
- `spark`: high-intensity challenge mode
- `pulse`: wellbeing/motivation support
- `atlas`: schedule and study-plan guidance

## API

- Endpoint: `POST /api/v1/chat`
- Request: `ChatRequest`
- Response: `ChatResponse` (includes `agent_name`, emoji/color cues)

## Manual Overrides

- `/test` -> `oracle`
- `/spark` -> `spark`
- `/chill` -> `pulse`
- `/plan` -> `atlas`
- `/veda` -> `veda`
- `/bye` -> finish

## Runtime

- Preferred: LangGraph state machine (`runtime_mode = "langgraph"`)
- Fallback: deterministic supervisor routing (`runtime_mode = "fallback"`)

