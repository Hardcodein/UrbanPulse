from enum import Enum


class PhaseStatus(Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    RUNNING = "RUNNING"
    FINISHED_OK = "FINISHED_OK"
    FINISHED_ERR = "FINISHED_ERR"