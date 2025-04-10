# Backend Setup

1. Create virtual environment:
   `python -m venv venv`

2. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   `pip install -r requirements.txt`

4. Run the server:
   `uvicorn main:app --reload`

The server will be available at `http://127.0.0.1:8000`.