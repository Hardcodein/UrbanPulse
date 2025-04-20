

from typing import Dict, List, Optional, Set

from Loader.Loader.Interfaces.IPhaseRepositoryStatus import IPhaseRepositoryStatus

from Loader.Loader.Models.PhaseStatus import PhaseStatus
from Loader.Loader.Models.Phase import Phase

class DataProvider:
    def __init__(self,
                 phase_status_store: IPhaseRepositoryStatus,
                 phases : List[Phase]
                 ):
        
        self.check_phases(phases)
        self._phase_status_store = phase_status_store
        self._phases = sorted(phases, key=lambda phase: phase.serial_number)[:]
        self._phase_name_to_phase_Dict: Dict[str, Phase] = {phase.name: phase for phase in phases}
        
    def check_phases(self, 
                     phases:List[Phase]):
        if len(phases) == 0:
            raise AssertionError("Ноль Phases. Должен быть хотя бы один")

        phase_names: Set[str] = {phase_item.name for phase_item in phases}

        if len(phase_names) != len(phases):
            raise AssertionError("Все этапы должные иметь одинаковые названия.")

        if not all(stage.serial_number >= 0 for stage in phases):
            raise AssertionError("Все порядковые номера должны быть положительными")

        phases = sorted(phases, key=lambda phase: phase.serial_number)[:]

        rigth_serial_numbers = range(len(phases))[:]

        for phase, right_order_number in zip(phases, rigth_serial_numbers):
            if phase.serial_number != right_order_number:
                raise AssertionError()
        
    def execute(self, 
                from_phase: Optional[str] = None, 
                to_phase: Optional[str] = None):
        # Проверка первой фазы
        if from_phase is None:
            start_phase = self._phases[0]

        elif from_phase in self._phase_name_to_phase_Dict:
            start_phase = self._phase_name_to_phase_Dict[from_phase]
        else:
            raise ValueError(f"Нет стадии=`{from_phase}`")
        
        # Проверка последней  фазы
        if to_phase is None:
            end_phase = self._phases[-1]

        elif to_phase in self._phase_name_to_phase_Dict:
            end_phase = self._phase_name_to_phase_Dict[to_phase]
        else:
            raise ValueError(f"Нет стадии=`{to_phase}`")

        if start_phase.serial_number > end_phase.serial_number:
            raise ValueError(f"Стадий находятся не по порядку")

        # Список всех статусов фаз
        phases_statuses_list = [
            self._phase_status_store.get_status_by_phase_name(phase.name)
            for phase in self._phases[:start_phase.serial_number]
        ]
        
       
        if not all(status is PhaseStatus.FINISHED_OK 
                   for status in phases_statuses_list):
            raise ValueError(f"Все стадии до =`{from_phase}` выполнены успешно.")
       
        # 
        for phase in self._phases[start_phase.serial_number:]:
            self._phase_status_store.set_status_by_phase_name(
                phase.name, PhaseStatus.NOT_EXECUTED)

        # Фазы для выполнения  Срез фаз для выполнения с начала и до конца
        phases_for_execute = self._phases[start_phase.serial_number:end_phase.serial_number + 1]

        # Пара выполнения итерации
        for item, phase in enumerate(phases_for_execute, start=1):
            print(f"Выполение фазы={item}/{len(phases_for_execute)}. Имя фазы=`{phase.name}`.")
            try:
                self._phase_status_store.set_status_by_phase_name(
                    phase.name, PhaseStatus.RUNNING)
                
                # Выполняем фазу. Через вызов метода
                phase.execution_method(*phase.execution_args)

                self._phase_status_store.set_status_by_phase_name(
                    phase.name, PhaseStatus.FINISHED_OK)
            except Exception as exception:
                self._phase_status_store.set_status_by_phase_name(
                    phase.name, PhaseStatus.FINISHED_ERR)
                raise

    # Возобновление выполнения процесса с последней успешно завершенной фазы
    def execute_from_last_excellent_phase(self):

        excellent_phases_list = [
            phase
            for phase in self._phases
            if self._phase_status_store.get_status_by_phase_name
            (phase.name) is PhaseStatus.FINISHED_OK
        ]

        if len(excellent_phases_list) != 0:

            last_successful_stage = excellent_phases_list[-1]

            if last_successful_stage.serial_number == len(self._phases) - 1:
                raise ValueError(f"Загрузчик остановился: "
                                 f"Последняя фаза `{last_successful_stage.name}`.")
            
            from_stage = self._phases[last_successful_stage.serial_number + 1].name
        else:
            from_stage = self._phases[0].name
        
        self.execute(from_stage)