# Product Requirements Document (PRD)
## CSV Data Visualizer

---

## 1. Overview

A tool that accepts a CSV file — either via file upload or piped from stdin — auto-detects column types, and generates interactive charts (bar, line, pie, scatter).

---

## 2. Core Features (MVP)

### 2.1 CSV Input
- **File upload:** drag-and-drop or file picker in the browser
- **Pipe from stdin:** accept CSV via `cat data.csv | python app.py` or `python app.py < data.csv`
- Accept only valid CSV; show clear error if file is malformed

### 2.2 Column Type Detection
Automatically detect and label each column as one of:
- **Number** — integers or floats
- **Date** — ISO dates, common formats (MM/DD/YYYY, etc.)
- **Category** — low-cardinality text (e.g. ≤ 20 unique values)
- **Text** — everything else

### 2.3 Interactive Charts
Generate all four chart types from detected columns:
- **Bar** — categorical X-axis, numeric Y-axis
- **Line** — continuous or time-series X-axis, numeric Y-axis
- **Pie** — single categorical column with count or numeric value
- **Scatter** — numeric X and Y axes

Chart requirements:
- Hover tooltips showing values
- Legend and axis labels
- Responsive sizing

---

## 3. Bonus Features

These are out of scope for MVP but worth building if time allows:

- **Filtering** — filter rows by column value before charting (range sliders, checkboxes, text search)
- **Column selection** — let users pick which columns map to X, Y, color, size
- **Export as PNG** — download the current chart as a high-resolution image
- **Dark mode** — toggle between light and dark themes, persisted to localStorage

---

## 4. Tech Stack

| Layer | Choice |
|-------|--------|
| Framework | Plotly Dash (Python) |
| Data | Pandas |
| Charts | Plotly |
| Styling | Dash Bootstrap Components |

---

## 5. Data Flow

```
CSV input (upload or stdin)
    ↓
Pandas reads file
    ↓
Column type detection
    ↓
User picks chart type
    ↓
Plotly renders chart
    ↓
[Bonus] User filters / selects columns / exports
```

---

## 6. Success Criteria

- CSV loads without errors (upload and pipe)
- Column types detected correctly for well-formed data
- All four chart types render with correct data mapping
- App runs locally with a single command

---

## 7. Out of Scope

- Authentication
- Database or persistent storage
- Cloud deployment
- Mobile-native app
- Real-time / collaborative features


this is important for the judging criteria so we need to follow this below
Judging Criteria — 25 Points Maximum Prompt Craft (1–5) — Clear scope, constraints, and done criteria in their Claude session. Used the prompt template structure. Gave Claude the right context without raw code      dumps.                                     
  
2. Working Output (1–5) — Does it run? Can you demo it live? Partial credit for clear, demonstrable progress. Broken builds with good prompting still score on other criteria.       
  
3. Creativity & Polish (1–5) — Went beyond the minimum. Surprising features, thoughtful UX, visual polish, clever edge-case handling. Shows imagination — not just completion.       
  
4. Presentation Clarity (1–5) — Can they explain their prompting decisions? What worked, what didn't? Clear walkthrough of their session start prompt and key pivots during the      
  build.                                     
  
5. Workflow Discipline (1–5) — Used git worktree. Proper session hygiene (no .env, no raw dumps). Clean git history. Followed the team workflow — not just "it works."