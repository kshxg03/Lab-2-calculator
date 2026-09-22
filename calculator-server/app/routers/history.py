from collections import deque
from typing import List
from fastapi import APIRouter, Depends

from app.schemas import CalculatorLog
from app.dependencies import get_history

router = APIRouter()


@router.get("/history", response_model=List[CalculatorLog])
def get_history_route(history: deque = Depends(get_history)):
    return list(history)


@router.delete("/history")
def clear_history_route(history: deque = Depends(get_history)):
    history.clear()
    return {"ok": True}