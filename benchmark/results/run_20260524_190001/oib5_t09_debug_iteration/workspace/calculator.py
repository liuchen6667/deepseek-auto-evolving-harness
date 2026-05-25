"""简单计算器 — 包含 3 个 bug"""


class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(("add", a, b, result))
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(("subtract", a, b, result))
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(("multiply", a, b, result))
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(("divide", a, b, result))
        return result

    def power(self, base, exp):
        result = base ** exp
        self.history.append(("power", base, exp, result))
        return result

    def get_history(self):
        return self.history.copy()

    def clear_history(self):
        self.history = []

    def average(self, numbers):
        if not numbers:
            raise ValueError("Cannot calculate average of empty list")
        return sum(numbers) / len(numbers)

    def factorial(self, n):
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        if n == 0:
            return 1
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
