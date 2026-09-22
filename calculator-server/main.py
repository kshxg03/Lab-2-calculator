import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

# Ensure calculator.py is in the same directory for this import to work
from calculator import expand_percent

history = deque(maxlen=1000)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})


@app.post("/calculate")
def calculate(expr: str):
    try:
        code = expand_percent(expr)
        result = aeval(code)
        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        
        # Save to history
        history.appendleft({"expr": expr, "result": result})
        
        return {"ok": True, "expr": expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": expr, "error": str(e)}


@app.get("/history")
def get_history(limit: int = 10):
    """
    Returns the calculation history.
    Use the 'limit' query parameter to specify how many records to fetch.
    """
    # Slice the deque up to the specified limit
    # Since history is a deque, we convert it to a list first to slice it cleanly
    return list(history)[:limit]


@app.delete("/history")
def clear_history():
    history.clear()
    return {"ok": True}
