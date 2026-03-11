"""Calculator tool for mathematical operations"""

import logging
from typing import Union

logger = logging.getLogger(__name__)


class Calculator:
    """Advanced calculator with scientific operations"""

    def __init__(self):
        self.last_result = None

    def add(self, x: float, y: float) -> float:
        """Add two numbers"""
        result = x + y
        self.last_result = result
        return result

    def subtract(self, x: float, y: float) -> float:
        """Subtract two numbers"""
        result = x - y
        self.last_result = result
        return result

    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers"""
        result = x * y
        self.last_result = result
        return result

    def divide(self, x: float, y: float) -> float:
        """Divide two numbers with zero check"""
        if y == 0:
            raise ValueError("Division by zero")
        result = x / y
        self.last_result = result
        return result

    def power(self, x: float, y: float) -> float:
        """Raise x to power y"""
        result = x ** y
        self.last_result = result
        return result

    def sqrt(self, x: float) -> float:
        """Square root"""
        if x < 0:
            raise ValueError("Cannot compute square root of negative number")
        result = x ** 0.5
        self.last_result = result
        return result

    def percentage(self, value: float, percent: float) -> float:
        """Calculate percentage of a value"""
        result = value * (percent / 100)
        self.last_result = result
        return result

    def evaluate(self, expression: str) -> float:
        """Safely evaluate a mathematical expression"""
        try:
            # Only allow safe operations
            allowed_names = {"__builtins__": {}}
            result = eval(expression, allowed_names)
            if not isinstance(result, (int, float)):
                raise ValueError(f"Expression must return a number, got {type(result)}")
            self.last_result = result
            return result
        except Exception as e:
            logger.error(f"Error evaluating expression '{expression}': {str(e)}")
            raise ValueError(f"Invalid expression: {str(e)}")

    def get_last_result(self) -> Union[float, None]:
        """Get the last calculated result"""
        return self.last_result
