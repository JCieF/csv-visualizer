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
