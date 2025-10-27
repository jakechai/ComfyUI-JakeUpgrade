#---------------------------------------------------------------------------------------------------------------------#
# Jake Math Operations Nodes for JK Custom Workflow of ComfyUI
#---------------------------------------------------------------------------------------------------------------------#
import math
import sys
import os
from typing import Any, Callable, Mapping, Tuple
from ..categories import icons

try:
    import simpleeval
except ImportError:
    raise ImportError("simpleeval package is required. Please install it with: pip install simpleeval")


DEFAULT_BOOL = ("BOOLEAN", {"default": False})
DEFAULT_STRING = ("STRING", {"default": ""})
DEFAULT_FLOAT = ("FLOAT", {"default": 0.0, "min": -sys.float_info.max, "max": sys.float_info.max, "step": 0.0001})
DEFAULT_INT = ("INT", {"default": 0, "min": -18446744073709551615, "max": 18446744073709551615, "step": 1})

# 布尔运算定义
BOOL_UNARY_OPERATIONS: Mapping[str, Callable[[bool], bool]] = {
    "Not": lambda a: not a,
}

BOOL_BINARY_OPERATIONS: Mapping[str, Callable[[bool, bool], bool]] = {
    "Or": lambda a, b: a or b,
    "Nor": lambda a, b: not (a or b),
    "Xor": lambda a, b: a ^ b,
    "Nand": lambda a, b: not (a and b),
    "And": lambda a, b: a and b,
    "Xnor": lambda a, b: not (a ^ b),
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
}

# 字符条件定义
STRING_BINARY_CONDITIONS: Mapping[str, Callable[[str, str], bool]] = {
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
}

# 浮点条件定义
FLOAT_UNARY_CONDITIONS: Mapping[str, Callable[[float], bool]] = {
    "IsZero": lambda a: a == 0.0,
    "IsPositive": lambda a: a > 0.0,
    "IsNegative": lambda a: a < 0.0,
    "IsNonZero": lambda a: a != 0.0,
    "IsPositiveInfinity": lambda a: math.isinf(a) and a > 0.0,
    "IsNegativeInfinity": lambda a: math.isinf(a) and a < 0.0,
    "IsNaN": lambda a: math.isnan(a),
    "IsFinite": lambda a: math.isfinite(a),
    "IsInfinite": lambda a: math.isinf(a),
    "IsEven": lambda a: a % 2 == 0.0,
    "IsOdd": lambda a: a % 2 != 0.0,
}

FLOAT_BINARY_CONDITIONS: Mapping[str, Callable[[float, float], bool]] = {
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
    "Gt": lambda a, b: a > b,
    "Gte": lambda a, b: a >= b,
    "Lt": lambda a, b: a < b,
    "Lte": lambda a, b: a <= b,
}

# 浮点数运算定义
FLOAT_UNARY_OPERATIONS: Mapping[str, Callable[[float], float]] = {
    "Neg": lambda a: -a,
    "Inc": lambda a: a + 1,
    "Dec": lambda a: a - 1,
    "Abs": lambda a: abs(a),
    "Sqr": lambda a: a * a,
    "Cube": lambda a: a * a * a,
    "Sqrt": lambda a: math.sqrt(a),
    "Exp": lambda a: math.exp(a),
    "Ln": lambda a: math.log(a),
    "Log10": lambda a: math.log10(a),
    "Log2": lambda a: math.log2(a),
    "Sin": lambda a: math.sin(a),
    "Cos": lambda a: math.cos(a),
    "Tan": lambda a: math.tan(a),
    "Asin": lambda a: math.asin(a),
    "Acos": lambda a: math.acos(a),
    "Atan": lambda a: math.atan(a),
    "Sinh": lambda a: math.sinh(a),
    "Cosh": lambda a: math.cosh(a),
    "Tanh": lambda a: math.tanh(a),
    "Asinh": lambda a: math.asinh(a),
    "Acosh": lambda a: math.acosh(a),
    "Atanh": lambda a: math.atanh(a),
    "Round": lambda a: round(a),
    "Floor": lambda a: math.floor(a),
    "Ceil": lambda a: math.ceil(a),
    "Trunc": lambda a: math.trunc(a),
    "Erf": lambda a: math.erf(a),
    "Erfc": lambda a: math.erfc(a),
    "Gamma": lambda a: math.gamma(a),
    "Radians": lambda a: math.radians(a),
    "Degrees": lambda a: math.degrees(a),
}

FLOAT_BINARY_OPERATIONS: Mapping[str, Callable[[float, float], float]] = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Mul": lambda a, b: a * b,
    "Div": lambda a, b: a / b,
    "Mod": lambda a, b: a % b,
    "Pow": lambda a, b: a**b,
    "FloorDiv": lambda a, b: a // b,
    "Max": lambda a, b: max(a, b),
    "Min": lambda a, b: min(a, b),
    "Log": lambda a, b: math.log(a, b),
    "Atan2": lambda a, b: math.atan2(a, b),
}

# 整数条件定义
INT_UNARY_CONDITIONS: Mapping[str, Callable[[int], bool]] = {
    "IsZero": lambda a: a == 0,
    "IsNonZero": lambda a: a != 0,
    "IsPositive": lambda a: a > 0,
    "IsNegative": lambda a: a < 0,
    "IsEven": lambda a: a % 2 == 0,
    "IsOdd": lambda a: a % 2 == 1,
}

INT_BINARY_CONDITIONS: Mapping[str, Callable[[int, int], bool]] = {
    "Eq": lambda a, b: a == b,
    "Neq": lambda a, b: a != b,
    "Gt": lambda a, b: a > b,
    "Lt": lambda a, b: a < b,
    "Geq": lambda a, b: a >= b,
    "Leq": lambda a, b: a <= b,
}

# 整数运算定义
INT_UNARY_OPERATIONS: Mapping[str, Callable[[int], int]] = {
    "Neg": lambda a: -a,
    "Abs": lambda a: abs(a),
    "Inc": lambda a: a + 1,
    "Dec": lambda a: a - 1,
    "Sqr": lambda a: a * a,
    "Cube": lambda a: a * a * a,
    "Not": lambda a: ~a,
    "Factorial": lambda a: math.factorial(a),
}

INT_BINARY_OPERATIONS: Mapping[str, Callable[[int, int], int]] = {
    "Add": lambda a, b: a + b,
    "Sub": lambda a, b: a - b,
    "Mul": lambda a, b: a * b,
    "Div": lambda a, b: a // b,
    "Mod": lambda a, b: a % b,
    "Pow": lambda a, b: a**b,
    "And": lambda a, b: a & b,
    "Nand": lambda a, b: ~a & b,
    "Or": lambda a, b: a | b,
    "Nor": lambda a, b: ~a & b,
    "Xor": lambda a, b: a ^ b,
    "Xnor": lambda a, b: ~a ^ b,
    "Shl": lambda a, b: a << b,
    "Shr": lambda a, b: a >> b,
    "Max": lambda a, b: max(a, b),
    "Min": lambda a, b: min(a, b),
}

class BoolToInt_JK:
    """Convert boolean value to integer (True=1, False=0)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("BOOLEAN", {"default": False, "tooltip": "Input boolean value to convert"})
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DESCRIPTION = "Convert boolean value to integer (True=1, False=0)"

    def op(self, a: bool) -> Tuple[int]:
        """Convert boolean to integer"""
        return (int(a),)


class IntToBool_JK:
    """Convert integer value to boolean (0=False, non-zero=True)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("INT", {"default": 0, "tooltip": "Input integer value to convert"})
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DESCRIPTION = "Convert integer value to boolean (0=False, non-zero=True)"

    def op(self, a: int) -> Tuple[bool]:
        """Convert integer to boolean"""
        return (a != 0,)

class FloatToInt_JK:
    """Convert float value to integer by truncating decimal part"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "tooltip": "Input float value to convert"})
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DESCRIPTION = "Convert float value to integer by truncating decimal part"

    def op(self, a: float) -> Tuple[int]:
        """Convert float to integer"""
        return (int(a),)

class IntToFloat_JK:
    """Convert integer value to float"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("INT", {"default": 0, "tooltip": "Input integer value to convert"})
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Conversion")
    DESCRIPTION = "Convert integer value to float"

    def op(self, a: int) -> Tuple[float]:
        """Convert integer to float"""
        return (float(a),)

class BoolUnaryOperation_JK:
    """Perform unary operations on boolean values (NOT operation)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(BOOL_UNARY_OPERATIONS.keys()), {"tooltip": "Select unary operation to perform"}),
                "a": ("BOOLEAN", {"default": False, "tooltip": "Input boolean value"})
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")
    DESCRIPTION = "Perform unary operations on boolean values (NOT operation)"

    def op(self, op: str, a: bool) -> Tuple[bool]:
        """Apply unary operation to boolean"""
        return (BOOL_UNARY_OPERATIONS[op](a),)

class BoolBinaryOperation_JK:
    """Perform binary operations on two boolean values (AND, OR, XOR, etc.)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(BOOL_BINARY_OPERATIONS.keys()), {"tooltip": "Select binary operation to perform"}),
                "a": ("BOOLEAN", {"default": False, "tooltip": "First boolean input"}),
                "b": ("BOOLEAN", {"default": False, "tooltip": "Second boolean input"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")
    DESCRIPTION = "Perform binary operations on two boolean values (AND, OR, XOR, etc.)"

    def op(self, op: str, a: bool, b: bool) -> Tuple[bool]:
        """Apply binary operation to two booleans"""
        return (BOOL_BINARY_OPERATIONS[op](a, b),)

class BoolBinaryAnd_JK:
    """Logical AND operation between two boolean values"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("BOOLEAN", {"default": False, "tooltip": "First boolean input"}),
                "b": ("BOOLEAN", {"default": False, "tooltip": "Second boolean input"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")
    DESCRIPTION = "Logical AND operation between two boolean values"

    def op(self, a: bool, b: bool) -> Tuple[bool]:
        """Apply AND operation"""
        return (a and b,)

class BoolBinaryOR_JK:
    """Logical OR operation between two boolean values"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("BOOLEAN", {"default": False, "tooltip": "First boolean input"}),
                "b": ("BOOLEAN", {"default": False, "tooltip": "Second boolean input"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Bool")
    DESCRIPTION = "Logical OR operation between two boolean values"

    def op(self, a: bool, b: bool) -> Tuple[bool]:
        """Apply OR operation"""
        return (a or b,)

class StringBinaryCondition_JK:
    """Compare two strings using binary conditions (equal, not equal)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(STRING_BINARY_CONDITIONS.keys()), {"tooltip": "Select comparison operation"}),
                "a": ("STRING", {"default": "", "tooltip": "First string input"}),
                "b": ("STRING", {"default": "", "tooltip": "Second string input"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/String")
    DESCRIPTION = "Compare two strings using binary conditions (equal, not equal)"

    def op(self, op: str, a: str, b: str) -> Tuple[bool]:
        """Apply binary condition to two strings"""
        return (STRING_BINARY_CONDITIONS[op](a, b),)

class FloatUnaryCondition_JK:
    """Check unary conditions on float values (zero, positive, negative, etc.)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_UNARY_CONDITIONS.keys()), {"tooltip": "Select unary condition to check"}),
                "a": ("FLOAT", {"default": 0.0, "tooltip": "Input float value to check"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")
    DESCRIPTION = "Check unary conditions on float values (zero, positive, negative, infinity, etc.)"

    def op(self, op: str, a: float) -> Tuple[bool]:
        """Apply unary condition to float"""
        return (FLOAT_UNARY_CONDITIONS[op](a),)

class FloatBinaryCondition_JK:
    """Compare two float values using binary conditions"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_BINARY_CONDITIONS.keys()), {"tooltip": "Select comparison operation"}),
                "a": ("FLOAT", {"default": 0.0, "tooltip": "First float input"}),
                "b": ("FLOAT", {"default": 0.0, "tooltip": "Second float input"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")
    DESCRIPTION = "Compare two float values using binary conditions (equal, greater than, less than, etc.)"

    def op(self, op: str, a: float, b: float) -> Tuple[bool]:
        """Apply binary condition to two floats"""
        return (FLOAT_BINARY_CONDITIONS[op](a, b),)

class FloatUnaryOperation_JK:
    """Perform unary mathematical operations on float values"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_UNARY_OPERATIONS.keys()), {"tooltip": "Select unary mathematical operation"}),
                "a": ("FLOAT", {"default": 0.0, "tooltip": "Input float value"}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")
    DESCRIPTION = "Perform unary mathematical operations on float values (abs, sqrt, sin, cos, etc.)"

    def op(self, op: str, a: float) -> Tuple[float]:
        """Apply unary operation to float"""
        try:
            result = FLOAT_UNARY_OPERATIONS[op](a)
            return (result,)
        except Exception as e:
            raise ValueError(f"Error applying operation {op} to value {a}: {str(e)}")

class FloatBinaryOperation_JK:
    """Perform binary mathematical operations on two float values"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(FLOAT_BINARY_OPERATIONS.keys()), {"tooltip": "Select binary mathematical operation"}),
                "a": ("FLOAT", {"default": 0.0, "tooltip": "First float input"}),
                "b": ("FLOAT", {"default": 0.0, "tooltip": "Second float input"}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Float")
    DESCRIPTION = "Perform binary mathematical operations on two float values (add, subtract, multiply, etc.)"

    def op(self, op: str, a: float, b: float) -> Tuple[float]:
        """Apply binary operation to two floats"""
        try:
            result = FLOAT_BINARY_OPERATIONS[op](a, b)
            return (result,)
        except Exception as e:
            raise ValueError(f"Error applying operation {op} to values {a} and {b}: {str(e)}")

class IntUnaryCondition_JK:
    """Check unary conditions on integer values (zero, positive, negative, even, odd)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(INT_UNARY_CONDITIONS.keys()), {"tooltip": "Select unary condition to check"}),
                "a": ("INT", {"default": 0, "tooltip": "Input integer value to check"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")
    DESCRIPTION = "Check unary conditions on integer values (zero, positive, negative, even, odd)"

    def op(self, op: str, a: int) -> Tuple[bool]:
        """Apply unary condition to integer"""
        return (INT_UNARY_CONDITIONS[op](a),)


class IntBinaryCondition_JK:
    """Compare two integer values using binary conditions"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(INT_BINARY_CONDITIONS.keys()), {"tooltip": "Select comparison operation"}),
                "a": ("INT", {"default": 0, "tooltip": "First integer input"}),
                "b": ("INT", {"default": 0, "tooltip": "Second integer input"}),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")
    DESCRIPTION = "Compare two integer values using binary conditions (equal, greater than, less than, etc.)"

    def op(self, op: str, a: int, b: int) -> Tuple[bool]:
        """Apply binary condition to two integers"""
        return (INT_BINARY_CONDITIONS[op](a, b),)

class IntUnaryOperation_JK:
    """Perform unary mathematical operations on integer values"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(INT_UNARY_OPERATIONS.keys()), {"tooltip": "Select unary mathematical operation"}),
                "a": ("INT", {"default": 0, "tooltip": "Input integer value"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")
    DESCRIPTION = "Perform unary mathematical operations on integer values (negate, increment, square, etc.)"

    def op(self, op: str, a: int) -> Tuple[int]:
        """Apply unary operation to integer"""
        try:
            result = INT_UNARY_OPERATIONS[op](a)
            return (result,)
        except Exception as e:
            raise ValueError(f"Error applying operation {op} to value {a}: {str(e)}")

class IntBinaryOperation_JK:
    """Perform binary mathematical operations on two integer values"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "op": (list(INT_BINARY_OPERATIONS.keys()), {"tooltip": "Select binary mathematical operation"}),
                "a": ("INT", {"default": 0, "tooltip": "First integer input"}),
                "b": ("INT", {"default": 0, "tooltip": "Second integer input"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")
    DESCRIPTION = "Perform binary mathematical operations on two integer values (add, subtract, multiply, etc.)"

    def op(self, op: str, a: int, b: int) -> Tuple[int]:
        """Apply binary operation to two integers"""
        try:
            result = INT_BINARY_OPERATIONS[op](a, b)
            return (result,)
        except Exception as e:
            raise ValueError(f"Error applying operation {op} to values {a} and {b}: {str(e)}")

class IntSubOperation_JK:
    """Subtract two integer values (a - b)"""
    
    @classmethod
    def INPUT_TYPES(cls) -> Mapping[str, Any]:
        return {
            "required": {
                "a": ("INT", {"default": 0, "tooltip": "First integer input (minuend)"}),
                "b": ("INT", {"default": 0, "tooltip": "Second integer input (subtrahend)"}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "op"
    CATEGORY = icons.get("JK/Math/Int")
    DESCRIPTION = "Subtract two integer values (a - b)"

    def op(self, a: int, b: int) -> Tuple[int]:
        """Subtract b from a"""
        return (a - b,)

class EvaluateFloats_JK:
    """Evaluate Python expressions with float variables and return multiple formats"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "python_expression": ("STRING", {
                    "default": "((a + b) - c) / 2", 
                    "multiline": False,
                    "tooltip": "Python expression using variables a, b, c (e.g., 'a + b * c')"
                }),
            },
            "optional": {
                "a": ("FLOAT", {
                    "default": 0, 
                    "min": -sys.float_info.max, 
                    "max": sys.float_info.max, 
                    "step": 0.0001,
                    "tooltip": "Float variable a for expression"
                }),
                "b": ("FLOAT", {
                    "default": 0, 
                    "min": -sys.float_info.max, 
                    "max": sys.float_info.max, 
                    "step": 0.0001,
                    "tooltip": "Float variable b for expression"
                }),
                "c": ("FLOAT", {
                    "default": 0, 
                    "min": -sys.float_info.max, 
                    "max": sys.float_info.max, 
                    "step": 0.0001,
                    "tooltip": "Float variable c for expression"
                }),
            },
        }

    RETURN_TYPES = ("INT", "FLOAT", "STRING")
    FUNCTION = "evaluate"
    CATEGORY = icons.get("JK/Math")
    DESCRIPTION = "Evaluate Python expressions with float variables and return results as INT, FLOAT, and STRING"

    def evaluate(self, python_expression, a=0, b=0, c=0):
        """Evaluate expression with float variables"""
        try:
            result = simpleeval.simple_eval(python_expression, names={'a': a, 'b': b, 'c': c})
            int_result = int(result)
            float_result = float(result)
            string_result = str(result)
            return (int_result, float_result, string_result)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{python_expression}': {str(e)}")

class EvaluateInts_JK:
    """Evaluate Python expressions with integer variables and return multiple formats"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "python_expression": ("STRING", {
                    "default": "((a + b) - c) / 2", 
                    "multiline": False,
                    "tooltip": "Python expression using variables a, b, c (e.g., 'a + b * c')"
                }),
            },
            "optional": {
                "a": ("INT", {
                    "default": 0, 
                    "min": -18446744073709551615, 
                    "max": 18446744073709551615, 
                    "step": 1,
                    "tooltip": "Integer variable a for expression"
                }),
                "b": ("INT", {
                    "default": 0, 
                    "min": -18446744073709551615, 
                    "max": 18446744073709551615, 
                    "step": 1,
                    "tooltip": "Integer variable b for expression"
                }),
                "c": ("INT", {
                    "default": 0, 
                    "min": -18446744073709551615, 
                    "max": 18446744073709551615, 
                    "step": 1,
                    "tooltip": "Integer variable c for expression"
                }),
            },
        }

    RETURN_TYPES = ("INT", "FLOAT", "STRING")
    FUNCTION = "evaluate"
    CATEGORY = icons.get("JK/Math")
    DESCRIPTION = "Evaluate Python expressions with integer variables and return results as INT, FLOAT, and STRING"

    def evaluate(self, python_expression, a=0, b=0, c=0):
        """Evaluate expression with integer variables"""
        try:
            result = simpleeval.simple_eval(python_expression, names={'a': a, 'b': b, 'c': c})
            int_result = int(result)
            float_result = float(result)
            string_result = str(result)
            return (int_result, float_result, string_result)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{python_expression}': {str(e)}")

class EvaluateStrs_JK:
    """Evaluate Python expressions with string variables and string operations"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "python_expression": ("STRING", {
                    "default": "a + b + c", 
                    "multiline": False,
                    "tooltip": "Python expression using string variables a, b, c (e.g., 'a + b + c' or 'len(a)')"
                }),
            },
            "optional": {
                "a": ("STRING", {
                    "default": "Hello", 
                    "multiline": False,
                    "tooltip": "String variable a for expression"
                }),
                "b": ("STRING", {
                    "default": " World", 
                    "multiline": False,
                    "tooltip": "String variable b for expression"
                }),
                "c": ("STRING", {
                    "default": "!", 
                    "multiline": False,
                    "tooltip": "String variable c for expression"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "evaluate"
    CATEGORY = icons.get("JK/Math")
    DESCRIPTION = "Evaluate Python expressions with string variables and string operations"

    def evaluate(self, python_expression, a="", b="", c=""):
        """Evaluate expression with string variables"""
        try:
            variables = {'a': a, 'b': b, 'c': c}
            functions = simpleeval.DEFAULT_FUNCTIONS.copy()
            functions.update({"len": len})  # Add string functions
            result = simpleeval.simple_eval(python_expression, names=variables, functions=functions)
            return (str(result),)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{python_expression}': {str(e)}")

class EvalExamples_JK:
    """Display examples for using evaluation nodes with various expressions"""
    
    @classmethod
    def INPUT_TYPES(cls):
        # Try to load examples from file
        examples_text = "Expression examples will be loaded from SimpleEval_Node_Examples.txt file"
        try:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SimpleEval_Node_Examples.txt')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    examples_text = file.read()
            else:
                examples_text = "Example file not found: SimpleEval_Node_Examples.txt"
        except Exception as e:
            examples_text = f"Error loading examples: {str(e)}"
            
        return {
            "required": {
                "models_text": ("STRING", {
                    "default": examples_text, 
                    "multiline": True,
                    "tooltip": "Examples of expressions for evaluation nodes"
                }), 
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "func"
    CATEGORY = icons.get("JK/Math")
    DESCRIPTION = "Display examples for using evaluation nodes with various expressions"

    def func(self, models_text):
        """Display examples (no output, just for documentation)"""
        return ()