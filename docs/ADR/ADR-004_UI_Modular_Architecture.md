# ADR-004: UI Modular Architecture and State Management

- **Status:** Accepted
- **Date:** 2026-03-03
- **Decision Owner:** Architect
- **Stage:** B
- **Related:** `app.py`, `app/ui/components.py`

## 1. Context
The Streamlit application entry point (`app.py`) had degraded into a monolithic script (~530 lines), heavily entangling business logic, remote execution orchestration, and UI rendering. Furthermore, session state initialization was scattered, leading to fragmented state checks throughout the codebase. This violated the separation of concerns principle and degraded maintainability.

## 2. Decision
We are refactoring the UI layer into a modular, declarative architecture:
1. **Separation of Concerns:** Extract all UI rendering logic into a dedicated package (`app/ui/components.py`).
2. **Centralized State:** Implement a single `init_session_state()` function called at application startup to initialize all required keys unconditionally.
3. **Reactive Rendering:** Utilize Streamlit's `@st.fragment` decorators for atomic UI components (e.g., command review buttons, sync triggers) to prevent full-page reruns and optimize performance.

## 3. Consequences
### Positive:
- `app.py` is reduced to a clean composition of high-level components (~320 lines).
- UI changes no longer risk breaking core SSH or logging logic.
- Partial reruns significantly decrease latency and unnecessary LLM/API re-initializations.
### Negative/Constraints:
- Developers must adhere to strict boundaries: no business logic in `app/ui`, no UI elements in `app/core`.