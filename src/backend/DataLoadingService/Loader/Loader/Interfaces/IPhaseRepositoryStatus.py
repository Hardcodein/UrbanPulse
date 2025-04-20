from abc import ABC,abstractmethod

from Loader.Models import PhaseStatus

class IPhaseRepositoryStatus(ABC):
    @abstractmethod
    def get_status_by_phase_name(self, 
                                 phase_name: str) -> PhaseStatus:
        pass

    @abstractmethod
    def set_status_by_phase_name(self, 
                                 phase_name: str, 
                                 phase_status: PhaseStatus) -> None:
        pass
