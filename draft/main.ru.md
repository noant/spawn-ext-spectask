# Spec-Tasks: AI-ориентированная методология разработки

## Структура папок

- spec/main.md — этот файл.
- spec/design.yaml — индекс архитектурных документов (`path` + `description` на запись); необязателен, но рекомендуется при нескольких файлах дизайна.
- spec/design/hla.md — высокоуровневая архитектура проекта (обязательно).
- spec/design/{name}.md — другие архитектурные документы (необязательно; ADR, заметки и т.д.); регистрируйте в **spec/design.yaml** и объявляйте как читаемые пути для агентов — обычно через `files:` расширения Spawn (с нужными reads), чтобы они попадали в `spawn/navigation.yaml`.
- spec/tasks/{task-code}-{slug}/ — папка задачи (дерево артефактов). `{task-code}` идентифицирует задачу (часто порядковый код; может быть ключом из внешнего трекера). `{slug}` — короткое описательное имя.
- spec/tasks/{task-code}-{slug}/overview.md — обзор задачи (обязательно).
- spec/tasks/{task-code}-{slug}/{N}-{description}.md — файлы подзадач (необязательно; обязательно, если `## Execution Scheme` определяет 2+ step).
- spec/seeds/{X}-{slug}.md — seed-файл (дерево артефактов в этом пакете методологии).

**Встроенные правила:**

Каждое правило имеет стабильный ярлык `[R{n}-{slug}]`. Ссылайтесь по ярлыку (например, `R10-ask`), а не по номеру — ярлык переживает перенумерацию.

_Гигиена папок_

1. **`R1-paths`** — в папке `spec/` допустимы только пути, разрешённые Структурой папок; никаких других файлов.
2. **`R2-no-clutter`** — не создавайте README и прочие лишние документы в `spec/` (частный случай `R1-paths`).

_Идентификация задачи_

3. **`R3-code-num`** — числовой `task-code`: предложите следующий номер (`R10-ask`) и ждите явного ответа перед созданием `spec/tasks/{task-code}-{slug}/`. Следующий номер = максимальный существующий `{task-code}` под `spec/tasks/` (включая `_DONE_`) плюс 1.
4. **`R4-code-tracker`** — `task-code` из внешнего трекера должен быть ключом тикета (например, `PROJ-123`). Сегменты после первого `-` могут содержать slug.

_Спеки задач_

5. **`R5-new-task`** — новые спек-задачи следуют Step 1 и шаблону обзора в конце файла.
6. **`R6-legacy-done`** — старые `spec/tasks/_DONE_*` могут предшествовать текущему шаблону; не копируйте их структуру, если она не совпадает с шаблоном.
7. **`R7-process`** — status-отметки `[V]` и подсказки пользователю должны точно повторять формулировки из соответствующего Step; Steps выполняются по порядку, если процесс явно не разрешает иное.
8. **`R8-concrete`** — спеки суть выполнимые правки, а не намерения: каждый обзор и подзадача называют конкретные пути и символы (пакеты/модули, классы, методы, функции) под изменением, а каждая пара Before / After в Code changes — огороженный минимальный фрагмент (реальные строки или точная замена) плюс строка поведения. Только prose или «изменить X на Y» без кода недопустимы. Self Spec Review считает отсутствие конкретных целей, неконкретные Before/After или нарушения шаблона дефектами до Step 3.
9. **`R9-greenfield`** — для новых символов та же дисциплина Before/After, что и в `R8-concrete`, с двумя отличиями: Before может быть только контекстом места вставки (цитировать нечего); After всё равно огороженный код плюс строка поведения.

_Взаимодействие и контекст_

10. **`R10-ask`** — когда нужно спросить пользователя (уточнения, подтверждения, выбор), используйте структурированный инструмент платформы (см. `R12-ask-tools`), предпочитая множественный выбор. Порядок запасных вариантов: инструмент платформы -> установленный MCP (elicitation) -> текстовый вопрос в чате.
11. **`R11-navigation`** — перед составлением спека откройте **`spawn/navigation.yaml`**, прочитайте все `read-required`, прочитайте задачно-релевантные `read-contextual` и примените их в спеке. Если файл отсутствует, правило — no-op (продолжайте). Self Spec Review повторно проверяет соответствие; нарушения — дефекты.
12. **`R12-ask-tools`** — инструменты запроса пользователя по платформам (данные для `R10-ask`):
    - **Cursor:** AskQuestion / cursor/ask_question
    - **VS Code/Copilot:** AskQuestions / vscode_askQuestions
    - **Claude Code:** AskUserQuestion; MCP elicitation/create
    - **Codex:** request_user_input
    - **Другие:** встроенный инструмент IDE или установленный MCP; запасной вариант — текстовый вопрос.
13. **`R13-model-line`** — каждый запрос подагента должен включать эту строку дословно:
    > End your final response with the line `My model: X` where X is your actual model identifier (e.g. `claude-sonnet-4-6`, `gpt-4o`) — write your actual model identifier in place of X.
    Записывая `[V]`/`[model-name]` после подагента: прочитайте последнюю строку его ответа, извлеките имя модели и впишите в скобки.

---

## Обзор процесса

```
[1] Spec created → [2] Self spec review → [3] Spec review (пользователь) → [4] Code implemented → [5] Self code review → [6] Code review / Debugging (пользователь) → [7] Design documents updated → (необязательно) извлечение паттернов в spawn/rules/
```

Отмечайте каждый status [V] по завершении. Оповещайте пользователя после steps 2, 5 и 6. После Step 7 предложите необязательное извлечение паттернов (не status-чекбокс).

---

## Step 1: Spec created

**Исполнитель:** AI-агент (текущий контекст)

1.1 **Правила проекта (navigation)** — **ОБЯЗАТЕЛЬНО!** Следуйте `R11-navigation` перед написанием содержимого спека.
1.2 **Уточнения реализации** — **ОБЯЗАТЕЛЬНО!** Перед написанием содержимого спека выявите неоднозначные, необязательные или зависящие от соглашений аспекты. Задайте пользователю явные вопросы (`R10-ask`) и ждите ответов. Зафиксируйте ответы (или согласованные умолчания) в **Details**. Пропускайте только при единственном очевидном пути реализации.
1.3 **Обзор дизайна** — в `overview.md` задачи добавьте раздел **Design overview**: затронутые модули; конкретные пути и символы (`R8-concrete`); изменения потока данных; точки интеграции.
1.4 **Обзор** — `spec/tasks/{task-code}-{slug}/overview.md` следует шаблону overview.md: разделы вплоть до `## Details` (примеры before/after и кода — туда); **Goal** = одно предложение. Добавляйте `## Execution Scheme` только при 2+ step.
1.5 **План выполнения** — при 2+ steps: идентификаторы steps в `## Execution Scheme` должны соответствовать именам файлов `{N}-{description}.md` из пункта 1.6.
1.6 **Декомпозиция** — создайте {N}-{description}.md для каждого step: цель, подход, затронутые файлы (с именованными классами/методами/функциями для каждого пути), изменения кода (before/after). Можно запустить **новый подагент** для анализа кодовой базы (только чтение), чтобы получить точный текст **Before** / **After**, затем вставить его выводы в файлы steps (только анализ; родительский агент владеет декомпозицией и спеком).

→ установить [V] "Spec created" `[model-name]` (запись модели по `R13-model-line`): `- [V] Spec created [model-name]`

---

## Step 2: Self spec review

**Исполнитель:** AI-агент (новый подагент)

Запрос подагента должен включать строку из `R13-model-line`.

Проверьте спек на: архитектурное воздействие, ошибки реализации, проблемы последовательности; убедитесь, что каждый step и обзор содержат конкретные файлы, модули и символы (классы, методы, функции) по `R8-concrete`; проверьте соответствие `R11-navigation`. Исправьте при необходимости.

→ установить [V] "Self spec review passed" `[model-name]` (запись модели по `R13-model-line`): `- [V] Self spec review passed [model-name]`
→ подсказка: "Self spec review passed — spec is ready for your review (Step 3). Reply 'spec review passed', 'lgtm', or 'ok' when satisfied."

---

## Step 3: Spec review

**Исполнитель:** Пользователь

После подтверждения ("spec review passed", "lgtm", "ok"):
→ установить [V] "Spec review passed"
→ подсказка: "Reply 'implement' to start."

---

## Step 4: Code implemented

**Исполнитель (координация):**
- **Тот же чат, что и Steps 1–2:** агент, создавший спек, не координирует Steps 4–5 сам. По команде реализации запустите **один новый подагент** — координатор Steps 4–5 целиком. Родительский агент ждёт подагента, затем ждёт пользователя для Step 6. Не открывайте отдельный чат вручную.
- **Свежий чат для выполнения** (Steps 1–2 отсутствуют в контексте): координатор — текущий агент.

**Координатор** — следует Execution Scheme, запускает по одному подагенту на step, затем Step 5.
**Каждый step в Execution Scheme:** AI-агент (новый подагент) — дочерний к координатору.

По команде "run it" / "implement" / "execute" / любой прямой инструкции начать реализацию:
0. Если "Spec review passed" ещё не отмечен, установить [V] "Spec review passed" автоматически — команда реализации подразумевает одобрение.
0a. Если в этом чате уже завершены Steps 1–2 для задачи: запустить подагент-координатор Steps 4–5 (см. Исполнитель выше) и прекратить координацию inline. В его запрос включить: следовать Steps 4–5 для `spec/tasks/{task-code}-{slug}/`; строку из `R13-model-line`.
1. ОБЯЗАТЕЛЬНО! Запускать подагент для каждого step — НЕ реализовывать inline. Без исключений, даже если step кажется тривиальным. Запрос подагента должен включать строку из `R13-model-line`.
2. Следовать Execution Scheme: → последовательно, || параллельно.

→ установить [V] "Code implemented" `[model-name]` координатора (запись модели по `R13-model-line`): `- [V] Code implemented [model-name]`; переименовать завершённые подзадачи в _DONE_ и проставить `Status: Done | model: {model}` в каждом файле подзадачи, взяв имя модели из ответа соответствующего подагента

---

## Step 5: Self code review

**Исполнитель:** AI-агент (новый подагент)

Запрос подагента должен включать строку из `R13-model-line`.

Проверьте все изменения: несоответствия, именование, отсутствующие импорты, нарушенные контракты. Исправьте при необходимости.

→ установить [V] "Self code review passed" `[model-name]` (запись модели по `R13-model-line`): `- [V] Self code review passed [model-name]`
→ подсказка: "Self review done. Reply 'code review passed' to proceed."

---

## Step 6: Code review / Debugging

**Исполнитель:** Пользователь

После подтверждения ("code review passed", "lgtm", "ok"):
→ установить [V] "Code Review / Debugging passed"
→ подсказка: "Will now update design documents (Step 7)."

---

## Последующие изменения после реализации

Если пользователь запрашивает доработку или исправления после Step 4:

1. Выполните изменения.
2. Спросите через `R10-ask`: "Do you want to update the specifications of the current task?"
   - Да: отредактируйте затронутые файлы подзадач и/или `overview.md` под фактическое состояние; не перезапускайте цикл спека.
   - Нет: продолжайте без изменений.

---

## Step 7: Design documents updated

**Исполнитель:** AI-агент (текущий контекст)

Не начинайте Step 7, пока не отмечен **Code Review / Debugging passed** (Step 6).

1. **Индекс** — прочитайте **spec/design.yaml**. Если отсутствует, применяется только **spec/design/hla.md** (Структура папок); добавьте **spec/design.yaml** при регистрации более одного пути в **spec/design/**.
2. **Область** — из подзадач, Execution Scheme и изменённых/добавленных файлов задачи выберите строки `path` под обновление; обновите нужные, остальные пропустите.
3. **Запись** — для каждого выбранного пути приведите markdown в соответствие с репозиторием после задачи; создайте файл, если он указан, но отсутствует.
4. Если задача добавила или переименовала архитектурные документы в **spec/design/**, обновите **spec/design.yaml** (`path` + `description` для каждого).
5. Переименуйте папку в _DONE_{task-code}-{name}.
6. Если Source seed Path в обзоре конкретен и указанный файл spec/seeds связан с этим обзором, переименуйте его один раз, добавив _DONE_.

→ установить [V] "Design documents updated" — вписать имя модели в скобки: `- [V] Design documents updated [model-name]`
→ перейти к **Необязательно: извлечение паттернов** ниже (тот же запуск при закрытии через Steps 6–7).

---

## Необязательно: извлечение паттернов (после Step 7)

**Исполнитель:** AI-агент (текущий контекст)

После Step 7 при желании извлеките многократно используемые подходы в **`spawn/rules/`** как кандидаты в стандарты проекта. Не status-пункт. Навык: **spectask-extract-patterns**.

Спросите один раз после Step 7, если в этом закрытии не было отказа.

### Критерии отбора (фильтр перед запросом)

Предлагайте только кандидатов, прошедших все условия:

1. **Многократное использование** — паттерн, подход или соглашение, полезное за пределами одной задачи (не разовая правка).
2. **Применимость** — может стать коротким правилом, которому агент способен следовать.
3. **Кандидат в стандарты** — правдоподобно как устойчивое соглашение проекта.
4. **Ещё не охвачено** — проверьте существующие **`spawn/rules/`**, строки правил **`spawn/navigation.yaml`** и связанные reads/файлы методологии Spawn на дубликаты или почти-дубликаты.
5. **Существующий код допустим** — паттерн, уже присутствующий в кодовой базе до задачи, но не зафиксированный в правилах, остаётся допустимым кандидатом. Не отклоняйте лишь потому, что задача его не вводила; обнаружения при закрытии достаточно.
6. **Примеры кода** — предпочитайте короткие реальные (или минимально реалистичные) фрагменты, демонстрирующие паттерн. Только prose — при необходимости.

Отклоняйте немедленно (не предлагайте):

- Специфическую для задачи проводку, идентификаторы тикетов, временные обходные решения
- Переформулировки HLA, языковых умолчаний или существующих правил
- Расплывчатые лозунги без применимого правила
- Идеи низкой ценности или спекулятивные (мусор)

Если после фильтрации кандидатов не осталось: кратко сообщите и остановитесь (не изобретайте заполнители).

### Запрос (`R10-ask`)

Задайте **один вопрос на каждого отфильтрованного кандидата** (короткий заголовок + однострочное обоснование). Варианты для каждого:

- **Required** — `read-required`
- **Optional** — `read-contextual`
- **Decline** — пропустить это правило

Ждите ответов. Записывайте только кандидатов, отмеченных Required или Optional, каждого с его областью видимости. Если все ответы — Decline (или кандидатов не было), ничего не записывайте.

### Запись

1. Записывайте в **`spawn/rules/`** (создайте папку при отсутствии).
2. Предпочитайте существующий файл **`spawn/rules/`** на ту же тему — объединяйте или пересматривайте его. Если подходящего нет, создайте новый Markdown-файл в kebab-case.
3. Предпочитайте короткие примеры кода в каждом правиле при применимости (критерий 6).
4. Добавляйте каждый файл в **`spawn/navigation.yaml`** под **`read-required` → `rules`** или **`read-contextual` → `rules`** по выбору пользователя. Строка: **`path`** + краткое **`description`** (не только hint). Никогда не перечисляйте один путь в обоих местах.
5. Выполните в терминале в точности **`spawn refresh`** — это применит новые правила в скиллах и файлах правил.

---

## Шаблон overview.md

```markdown
# {task-code}: {Title}

## Source seed
- Path: {seed path or none}

## Status
- [ ] Spec created [model]
- [ ] Self spec review passed [model]
- [ ] Spec review passed
- [ ] Code implemented [model]
- [ ] Self code review passed [model]
- [ ] Code Review / Debugging passed
- [ ] Design documents updated [model]

## Goal
{One concise sentence.}

## Design overview
- Affected modules: {list}
- Files & symbols (concrete paths; class / method / function / module names to touch): {list}
- Data flow changes: {description}
- Integration points: {list}

## Before -> After
### Before
- {current state}
### After
- {desired state}

## Details
{Clarifying details, code examples, constraints.}

## Execution Scheme
> Each step id is the subtask filename (e.g. `1-abstractions`).
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions -- even if a step seems trivial or small.
- Phase 1 (sequential): step {N}-{description} -> step {N}-{description}
- Phase 2 (parallel):   step {N}-{description} || step {N}-{description}
- Phase 3 (sequential): step review -- inspect all changes, fix inconsistencies
```

Опустите `## Execution Scheme`, если декомпозиции нет (спек в одном файле).

---

## Шаблон файла подзадачи

Имя файла совпадает с идентификатором step из `## Execution Scheme` (например, `1-abstractions.md`). Один файл на step.

````markdown
# Step {N}: {Short title}

Status: Not implemented | model: {model}

## Goal
{One sentence -- outcome of this step.}

## Approach
{Order of work, constraints, references to spec/design if needed.}

## Affected files
- `{path/relative/to/repo/root}`
- `{...}` -- {...}

## Code changes (before / after)

### `{path/to/file.ext}` -- {path plus named symbols (module, class, method, or function) + what changes}

**Before**
```code
{concrete minimal excerpt or exact lines, not vague prose}
```
{what this code does -- behavior, not a repeat of the diff}

**After**
```code
{replacement or new block -- one-to-one with Before when editing existing text}
```
{what the new code does -- behavior, not a repeat of the diff}

### `{path/to/other.ext}` -- {where}
**Before**
```code
{concrete minimal excerpt or exact lines, not vague prose}
```
{what this code does -- behavior, not a repeat of the diff}
**After**
```code
{replacement or new block -- one-to-one with Before when editing existing text}
```
{what the new code does -- behavior, not a repeat of the diff}

## Additional actions
{Optional: shell commands, manual verification steps, follow-up tasks, or other non-file-edit work for this step.}
````

---

**Seed** — необязательно: Markdown-файл в `spec/seeds/` для быстрой фиксации идеи; Steps 1–7 не требуют его, если вы намеренно не начинаете оттуда. Ссылайтесь из `overview.md` при продвижении в spectask; применяйте пункт 6 Step 7 при закрытии связанного seed.

## Шаблон seed-файла (заголовок)

```markdown
linked task: {task path or none}

{idea content}
```
