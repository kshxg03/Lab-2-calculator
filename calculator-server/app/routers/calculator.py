import math
from datetime import datetime, timezone
from collections import deque
from fastapi import APIRouter, Depends
from asteval import Interpreter

from app.schemas import Expression
from app.dependencies import expand_percent, get_history

router = APIRouter()
aeval = Interpreter(minimal=True, usersyms={"pi": math.pi, "e": math.e})


@router.post("/calculate")
def calculate(req: Expression, history: deque = Depends(get_history)):
    try:
        code = expand_percent(req.expr)
        result = aeval(code)

        if aeval.error:
            msg = "; ".join(str(e.get_error()) for e in aeval.error)
            aeval.error.clear()
            return {"ok": False, "expr": req.expr, "result": "", "error": msg}

        log_entry = {
            "timestamp": datetime.now(timezone.utc),
            "expr": req.expr,
            "result": result,
        }
        history.appendleft(log_entry)

        return {"ok": True, "expr": req.expr, "result": result, "error": ""}
    except Exception as e:
        return {"ok": False, "expr": req.expr, "error": str(e)}