# Product Requirements Document (PRD)
## CSV Data Visualizer

**Version:** 1.1
**Status:** In Progress
**Last Updated:** 2026-03-19

---

## 1. Problem Statement

Data analysts, developers, and non-technical users frequently need to explore CSV data without setting up a full BI tool or writing ad-hoc scripts. There is no lightweight, zero-config tool that lets someone drag in a CSV and immediately get interactive, shareable charts.

**This tool solves that.** Upload a CSV, get instant interactive visualizations — no code, no setup, no account.

---

## 2. Target Users

| Persona | Description | Primary Need |
|---|---|---|
| **Data Analyst** | Explores datasets daily, comfortable with spreadsheets | Fast exploratory charting without writing code |
| **Developer** | Builds or debugs data pipelines | Quick sanity-check on CSV output |
| **Non-technical Stakeholder** | Receives CSV reports, limited technical skills | Self-service visualization without asking for help |

---

## 3. User Stories

- As a **user**, I want to upload a CSV file so that I can explore its contents visually.
- As a **user**, I want the app to auto-detect column types so that I don't have to configure anything before charting.
- As a **user**, I want to choose from multiple chart types so that I can represent my data appropriately.
- As a **user**, I want to select which columns map to X and Y axes so that I have control over what's visualized.
- As a **user**, I want to filter rows by column value so that I can focus on a subset of my data.
- As a **user**, I want to toggle dark mode so that the app is comfortable to use in low-light environments.
- As a **user**, I want to export the current chart as a PNG so that I can share it without screenshots.
- As a **developer**, I want to pipe CSV from stdin so that I can integrate this into a CLI workflow.

---

## 4. Functional Requirements

### 4.1 CSV Input

| ID | Requirement | Priority |
|---|---|---|
| F-01 | Accept CSV via drag-and-drop or file picker in the browser | Must |
| F-02 | Accept CSV piped from stdin (`cat data.csv \| python app.py`) | Should |
| F-03 | Display a clear, human-readable error if the file is malformed or not a valid CSV | Must |
| F-04 | Support files up to 50MB | Must |

**Acceptance Criteria — F-01:**
- User can drag a `.csv` file onto the upload zone and see it load within 3 seconds for files under 10MB.
- A success message with filename is shown after upload.

**Acceptance Criteria — F-03:**
- Malformed CSV shows an inline error message (not a crash or blank screen).

---

### 4.2 Column Type Detection

| ID | Requirement | Priority |
|---|---|---|
| F-05 | Detect and label each column as: Number, Date, Category, or Text | Must |
| F-06 | Category = text column with ≤ 20 unique values | Must |
| F-07 | Support common date formats: ISO 8601, MM/DD/YYYY, DD-MM-YYYY | Should |

**Acceptance Criteria — F-05:**
- For a well-formed CSV, all columns are detected correctly with no manual intervention.
- Detection results are reflected immediately in axis selectors and filter controls.

---

### 4.3 Interactive Charts

| ID | Requirement | Priority |
|---|---|---|
| F-08 | Support four chart types: Bar, Line, Pie, Scatter | Must |
| F-09 | Axis selectors populated dynamically based on detected column types | Must |
| F-10 | Charts include hover tooltips, axis labels, and legend | Must |
| F-11 | Charts are responsive and resize with the browser window | Must |

**Acceptance Criteria — F-08/F-09:**
- Bar: categorical X-axis, numeric Y-axis options only.
- Line: continuous or datetime X-axis, numeric Y-axis.
- Pie: single categorical column, value or count aggregation.
- Scatter: numeric X and Y axes only.
- Selecting an incompatible axis type is prevented or shows a warning.

---

### 4.4 Filtering

| ID | Requirement | Priority |
|---|---|---|
| F-12 | Range slider for numeric columns | Could |
| F-13 | Multi-select dropdown for categorical columns | Could |
| F-14 | Filters apply without page reload; chart updates reactively | Must (if filtering is present) |

---

### 4.5 Theme & Export

| ID | Requirement | Priority |
|---|---|---|
| F-15 | Dark mode toggle, persisted across page refreshes | Could |
| F-16 | Export active chart as PNG | Could |

---

## 5. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NF-01 | Chart render time after axis selection | < 1 second for files under 10MB |
| NF-02 | CSV parse time on upload | < 3 seconds for files under 10MB |
| NF-03 | Browser support | Latest Chrome, Firefox, Safari |
| NF-04 | App startup | Single command: `python app.py` |
| NF-05 | No authentication, no persistent storage, no external APIs | Hard constraint |

---

## 6. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Framework | Plotly Dash >= 2.14 | Reactive Python web framework, no JS required |
| UI Components | Dash Bootstrap Components >= 1.5 | Bootstrap layout + dark mode support |
| Data Handling | Pandas >= 2.1 | Industry-standard CSV/DataFrame tooling |
| Charts | Plotly >= 5.18 | Interactive charts with built-in PNG export |
| Language | Python 3.9+ | Broad compatibility, team familiarity |

---

## 7. Data Flow

```
CSV input (upload or stdin)
    ↓
Pandas parses & validates file
    ↓
Column type detection (Number / Date / Category / Text)
    ↓
User selects chart type + axis columns
    ↓
[Optional] User applies filters
    ↓
Plotly renders interactive chart
    ↓
[Optional] User exports chart as PNG
```

---

## 8. Out of Scope

- Authentication or user accounts
- Database or persistent storage
- Cloud deployment
- Mobile-native app
- Real-time or collaborative features
- CSV editing or data cleaning

---

## 9. Assumptions & Constraints

- CSV files are well-formed UTF-8 encoded text.
- The app runs locally; no network latency concerns.
- No accessibility (WCAG) compliance required for MVP.
- Python environment with dependencies installed (`pip install -r requirements.txt`).

---

## 10. Success Criteria

| Metric | Target |
|---|---|
| CSV loads without errors (upload + pipe) | 100% of well-formed files |
| Column type detection accuracy | ≥ 95% on well-formed datasets |
| All four chart types render correctly | Pass all chart acceptance criteria |
| App starts with a single command | `python app.py` with no extra config |
| Zero unhandled exceptions in normal use | No crash on valid input |
