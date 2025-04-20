from pathlib import Path

from Loader.Interfaces import IPhaseRepositoryStatus
from Loader.Loader.Models import PhaseStatus

class FilePhaseStatusStore(IPhaseRepositoryStatus):
    def __init__(self,dataFolderPath : Path):
        if dataFolderPath.is_file():
            raise AssertionError(f"{dataFolderPath} не директория. Это файл")
        
        dataFolderPath.mkdir(exist_ok=True, 
                             parents=True)

        self.datafolderpath = dataFolderPath

    def set_status_by_phase_name(self, 
                                 phase_name: str, 
                                 phase_status: PhaseStatus) -> None:
        #Проверка аргументов на соответствие типов
        if not isinstance(phase_name, str):
            raise ValueError(f'Phase_Name неверна =`{phase_name}`. '
                             f'Phase_name должна быть типа строки без пробелов')
        #Проверка аргументов на соответствие типов
        if not isinstance(phase_status, 
                          PhaseStatus):
            raise ValueError(f'Неверное значение PhaseStatus. '
                             f'`Ожидался тип PhaseStatus , но введен тип = {type(phase_status)}')
        
         #Присвоение пути к файлу статусов
        filepath = self.datafolderpath / f'{phase_name.lower()}.status'

         #Запись в файл статуса
        with open(str(filepath), 'w') as file:
            file.write([phase_status].value)


    def get_status_by_phase_name(self, 
                                 phase_name: str) -> PhaseStatus:
        #Проверка аргументов на соответствие типов
        if not isinstance(phase_name, str):
             raise ValueError(f'Phase_Name неверна =`{phase_name}`. '
                              f'Phase_name должна быть типа строки без пробелов')
        
        #Присвоение пути к файлу статусов
        filepath = self.datafolderpath / f'{phase_name.lower()}.status'

        if not filepath.exists():
            return PhaseStatus.NOT_EXECUTED

        with open(str(filepath), 'r') as file:
            localstatus = file.read()

        return PhaseStatus(localstatus)

        


    
        

