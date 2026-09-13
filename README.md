# Ola Domain Support Agent

Ola Business Operations / Customer Support capstone.

## Python
Use Python 3.11 on Windows.

## Installation
```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process      
.\venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run order
```powershell
python dataset.py
python -m app.pipeline build
python -m app.pipeline calibrate
python -m app.pipeline evaluate_rag
python -m app.pipeline demo
python -m app.review

uvicorn app.main:app --reload
```
API documentation: http://127.0.0.1:8000/docs

Run all tests:
```powershell
pytest -q
```

## Part 1 - Task 1 Dataset design choices
SEED = 260113
CATEGORY_WEIGHTS = [0.22, 0.22, 0.18, 0.18, 0.20]
STATUS_WEIGHTS = [0.24, 0.28, 0.12, 0.22, 0.14]
RESOLUTION_HOURS = (2, 72)

** Keep `MOCK_LLM=true` for the graded, zero-key path.
** Run MOCK_LLM variable as true for graded evaluation.
** All 12 policy documents are in a single file named policy.md under the data folder.
** While using "/add-document" endpoint, the file doesn't actually get updated on the policy.md file.
** To change the style of chucking, in pipeline.py file, change line 68 from  "hits=retrieve_top(query,'sentence',3)" to        "hits=retrieve_top(query,'fixed',3)"
** on testing for "What is the SLA for Sev-1 tickets?", it retrieves a wrong document when used fixed chucking. 
But, when the chunking strategy is changed to sentence based chunking, it retrieves the correct document.
