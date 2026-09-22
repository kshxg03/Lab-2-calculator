import math
from collections import deque
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asteval import Interpreter

from calculator import expand_percent

history = deque(maxlen=1000)

app = FastAPI(title="Mini Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared clean symbol dictionary
MATH_SYMBOLS = {"pi": math.pi, "e": math.e}


@app.post("/calculate")
def calculate(expr: str):
    # CRITICAL FIX: Instantiate an isolated Interpreter per network request.
    # This prevents parallel request overlaps from polluting or bypassing the error check.
    local_eval = Interpreter(minimal=True, usersyms=MATH_SYMBOLS)
    
    try:
        code = expand_percent(expr)
        result = local_eval(code)
        
        # Verify if an evaluation error occurred during this specific run
        if local_eval.error:
            msg = "; ".join(str(e.get_error()) for e in local_eval.error)
            return {"ok": False, "expr": expr, "result": "", "error": msg}
        
        # If result is None but no error occurred, ensure it's handled safely
        if result is None:
            return {"ok": False, "expr": expr, "result": "", "error": "Invalid mathematical expression"}

        # Build structural mapping consistency for your JS frontend (`expr` instead of `lhs`)
        history_item = {"expr": expr, "result": result}
        
        # Clean state control: Ensure this exact entry isn't accidentally duplicated
        if not history or history[0] != history_item:
            history.appendleft(history_item)
        
        return {"ok": True, "expr": expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": expr, "error": str(e)}


@app.get("/history")
def get_history(limit: int = 10):
    """
    Returns the calculation history.
    """
    return list(history)[:limit]



@app.delete("/history")
def clear_history():
    history.clear()
    return {"ok": True}
