# ADR-005: Core/UI Architecture Cleanup and Dependency Injection

- **Status:** Accepted
- **Date:** 2026-03-05
- **Decision Owner:** Architect
- **Stage:** B
- **Related:**
  - ADR-004: UI Modular Architecture and State Management
  - `app/streamlit_app.py`, `app/ui/components.py`, `app/core/pipeline.py`

---

## 1. Context

После первичного рефакторинга (ADR-004) приложение имело ряд структурных проблем:

1. **Два файла-точки входа** — `app.py` (330 строк) и `app/streamlit_app.py` (317 строк) существовали
   параллельно с дублирующимися функциями `call_gemini`, `process_parsed_tags`,
   `generate_image_with_imagen`. Изменения приходилось вносить в оба места.

2. **`process_parsed_tags` со side-effect'ами** — функция, вызываемая как LLM-запрос, внутри
   делала git commit, записывала ADR-файлы и загружала изображения на VM, при этом вызывая
   `st.toast / st.error / st.spinner`. Тестировать и переиспользовать без запущенного Streamlit
   было невозможно.

3. **Бизнес-логика в UI-компонентах** — `components.py` напрямую импортировал и вызывал
   `execute_ssh` из `ssh_executor`. Логика выполнения команд была разбросана по трём местам:
   `_render_foreman_command_buttons`, `_render_critic_command_review` и `pipeline.py`.

4. **Несогласованная модель данных истории** — `orch_history` хранил сырые строки (`"$ cmd\nout"`),
   тогда как все остальные истории использовали `[{"role", "content"}]`. `critic_history`
   инициализировался, но никогда не использовался.

5. **DI через длинные сигнатуры** — `render_foreman_column` принимал 7 параметров.
   `pipeline.run_pipeline` принимал `call_gemini_fn` как callback именно из-за отсутствия
   контейнера зависимостей.

---

## 2. Decision Drivers

- **Тестируемость**: core-модули не должны зависеть от Streamlit.
- **DRY**: каждый кусок логики существует ровно в одном месте.
- **Maintainability**: изменение точки выполнения SSH-команды или LLM-интерфейса должно
  требовать правки в одном файле, а не в трёх.
- **Явные зависимости**: компонент должен объявлять зависимости через параметры, а не
  закрывать их по замыканию.

---

## 3. Considered Options

### Option A — Сохранить текущую структуру, добавить комментарии
- Summary: задокументировать проблемные места без рефакторинга.
- Pros: нулевой риск регрессий.
- Cons: проблемы остаются и накапливаются.

### Option B — Снести `app.py`, ввести `AppContext`, разделить слои (выбрано)
- Summary: единая точка входа, контейнер зависимостей, чистые core-функции.
- Pros: решает все пять проблем выше, не ломает публичный API компонентов снаружи.
- Cons: требует согласованных правок в нескольких файлах одновременно.

### Option C — Перейти на FastAPI + React
- Summary: полностью отказаться от Streamlit.
- Pros: нет ограничений Streamlit-модели.
- Cons: несоразмерно объёму задачи, потребует переписывания всего UI.

---

## 4. Decision

Принят **Option B**. Выполнен следующий набор изменений:

### 4.1 Единая точка входа
- Удалён `app.py` (дублировал `app/streamlit_app.py`).
- `streamlit_app.py` добавляет корень проекта в `sys.path` через `__file__`, что позволяет
  запускать `streamlit run app/streamlit_app.py` из любого рабочего каталога.
- `_init_gcp()` расширен: резолвит `PROJECT_ID` и `VM_IP` через Compute API (логика,
  которая ранее была только в `app.py`), возвращает 4 значения вместо 3.

### 4.2 `core/image_generator.py`
Функция `generate_image_with_imagen()` вынесена из `streamlit_app.py` в отдельный модуль
без зависимостей на Streamlit. Вызывается из UI через `with st.spinner(...)`.

### 4.3 `core/tag_processor.py` — `TagResult`
```
process_parsed_tags(tags)      →  process_tags(tags, *, upload_fn, history_fn, image_fn)
  возвращал str                →    возвращает TagResult(notifications, errors, extra_text)
  вызывал st.toast/st.error    →    не знает о Streamlit
  делал git commit             →    делает git commit (side-effect оправдан)
```
`streamlit_app.py` содержит тонкую UI-обёртку `process_parsed_tags()`, которая вызывает
`process_tags()` и рендерит `result.notifications` → `st.toast`, `result.errors` → `st.error`.

### 4.4 Унификация историй
| История | Было | Стало |
|---|---|---|
| `orch_history` | `list[str]` | `list[{"role", "content"}]`, role = `"orchestrator"` / `"system"` |
| `critic_history` | инициализировался, не использовался | записывает каждую проверку (submit/approve/revision/cancel) и рендерится в верхнем контейнере колонки Критика |

Миграция: `init_session_state()` конвертирует старые строки в dict при каждом старте
сессии — обратная совместимость с JSON-файлами сохранена.

### 4.5 `execute_command` в `pipeline.py`
Добавлена функция-обёртка `execute_command(bash_command, credentials, oslogin_service)`.
`components.py` больше не импортирует `ssh_executor` напрямую.

Единственный путь выполнения команды из UI:
```
components.py → pipeline.execute_command() → ssh_executor.execute_ssh()
```

### 4.6 `core/app_context.py` — `AppContext`
```python
@dataclass
class AppContext:
    call_gemini: Callable
    skill_manager: Any
    credentials: Any
    oslogin_service: Any
    get_ssh_recent_memory_fn: Optional[Callable] = None
```
Создаётся один раз в `streamlit_app.py` после `_init_gcp()`. Передаётся во все
render-функции единственным аргументом.

До / после сигнатур:
```python
# До
render_foreman_column(call_gemini_fn, validate_bash_fn, search_skills_fn,
                      skill_manager, credentials, oslogin_service,
                      get_ssh_recent_memory_fn=None)
run_pipeline(bash_command, call_gemini_fn, skill_manager,
             credentials, oslogin_service, exec_timeout, on_step)

# После
render_foreman_column(ctx: AppContext)
run_pipeline(bash_command, ctx: AppContext, exec_timeout, on_step)
```

`pipeline.py` импортирует `AppContext` только под `TYPE_CHECKING` — нет runtime
circular-import между `core/` модулями.

---

## 5. Consequences

### Положительные
- Каждый core-модуль (`tag_processor`, `image_generator`, `pipeline`) тестируется
  независимо от Streamlit.
- Добавление нового render-компонента требует только `ctx: AppContext` — никаких
  изменений в точке вызова.
- Логика выполнения SSH живёт в одном месте: `pipeline.py`.
- `critic_history` даёт Критику полный audit trail проверок внутри сессии.

### Ограничения / риски
- `call_gemini` в `AppContext` остаётся функцией app-уровня (знает о Streamlit через
  `process_parsed_tags`). Это сознательный компромисс: полное разделение потребует
  рефакторинга `GeminiInterface` — вынесено за рамки этого ADR.
- Добавление новой зависимости требует расширения `AppContext` — это явное и
  контролируемое изменение.
