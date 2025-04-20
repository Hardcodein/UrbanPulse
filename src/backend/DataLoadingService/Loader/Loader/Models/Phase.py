from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Phase:
    name: str
    description: str
    serial_number: int
    execution_method: Callable
    execution_args: Any