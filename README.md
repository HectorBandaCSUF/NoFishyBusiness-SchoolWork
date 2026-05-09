# NoFishyBusiness

A locally-hosted, AI-assisted aquarium information web application. It provides fish care sheets, tank setup guidance, water chemistry analysis, maintenance schedules, and a conversational AI assistant — all grounded in a local SQLite knowledge base via a RAG pipeline.

---

## Setup and Run Instructions

### Prerequisites

- Python 3.11 or higher
- An OpenAI API key (gpt-4o-mini access required)

### Steps

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd NoFishyBusiness-SchoolWork
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - On macOS / Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - On Windows (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure your API key**

   ```bash
   cp .env.example .env
   ```

   Open `.env` and replace `your-openai-api-key-here` with your actual OpenAI API key:

   ```
   OPENAI_API_KEY=sk-...
   ```

6. **Populate the knowledge base** (first run only)

   ```bash
   python knowledge_base/seed.py
   ```

7. **Start the backend** (Terminal 1)

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

8. **Start the frontend** (Terminal 2)

   ```bash
   streamlit run frontend/app.py
   ```

   The app will open automatically at `http://localhost:8501`.

---

## Running Tests

```bash
pytest tests/
```

## Running the Evaluation Suite

Make sure the backend is running (step 7), then:

```bash
python eval/eval.py
```

---

## Project Structure

```
NoFishyBusiness/
├── backend/           # FastAPI backend — API routes, RAG, tools
│   └── tools/         # Individual tool implementations
├── frontend/          # Streamlit frontend
│   └── pages/         # One page per tool
├── knowledge_base/    # SQLite database and seed script
├── eval/              # Evaluation script and labeled test cases
├── tests/             # Unit and property-based tests
├── .env.example       # API key template
└── requirements.txt   # Pinned Python dependencies
```
