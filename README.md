# EduReport — Student Report Generator

A web-based system that generates beautiful, print-ready student reports from an Excel file.

## Setup

### 1. Install Dependencies
```bash
pip install flask pandas openpyxl
```

### 2. Run the Server
```bash
cd report_system
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

---

## How to Use

1. **Fill in school info** — Enter your school name, term, and year
2. **Upload Excel file** — Drag & drop or browse for your `.xlsx` file
3. **View reports** — All student reports are generated instantly
4. **Print** — Click "Print All Reports" to print or save as PDF

---

## Excel File Format

Your Excel sheet must have these column headers (case-insensitive):

| Column | Description |
|--------|-------------|
| NAME | Student's full name |
| REG NO | Registration number |
| CLASS | Class/stream (e.g. S.4A) |
| COMMENT | Teacher's remark |
| ONLINE ASSESSMENT | Score from online test |
| PHYSICAL EXAM | Score from physical exam |
| TOTAL | Combined total score |
| SIGNATURE | Teacher's name/signature |

A sample file `sample_students.xlsx` is included.

---

## Grading Scale

| Total | Grade | Description |
|-------|-------|-------------|
| 90–100 | A+ | Distinction |
| 80–89 | A | Excellent |
| 70–79 | B | Very Good |
| 60–69 | C | Good |
| 50–59 | D | Average |
| Below 50 | F | Below Average |

---

## Project Structure

```
report_system/
├── app.py                 # Flask backend
├── templates/
│   ├── index.html         # Upload page
│   └── report.html        # Report display & print page
├── uploads/               # Temporary Excel file storage
├── sample_students.xlsx   # Sample data
└── README.md
```
