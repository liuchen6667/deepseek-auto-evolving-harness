"""简单计算器 — 修复所有 bug"""


class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(("add", a, b, result))
        return result

    def subtract(self, a, b):
        # 修复 BUG 1: 减法方向正确应为 a - b
        result = a - b
        self.history.append(("subtract", a, b, result))
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(("multiply", a, b, result))
        return result

    def divide(self, a, b):
        # 修复 BUG 2: 使用浮点数除法，处理除零
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
        # 返回历史记录的副本，防止外部修改内部状态
        return self.history.copy()

    def clear_history(self):
        self.history = []

    def average(self, numbers):
        # 修复 BUG 3: 处理空列表，返回浮点数
        if not numbers:
            raise ValueError("Cannot compute average of empty list")
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
