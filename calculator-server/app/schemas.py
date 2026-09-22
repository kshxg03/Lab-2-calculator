from datetime import datetime
from pydantic import BaseModel


class BaseExpression(BaseModel):
    expr: str


class Expression(BaseExpression):
    """ExpressionIn model."""
    pass


class CalculatorLog(BaseExpression):
    """ExpressionOut model."""
    timestamp: datetime
    result: float | str