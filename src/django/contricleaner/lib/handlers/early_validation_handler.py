from contricleaner.lib.dto.list_dto import ListDTO


class EarlyValidationHandler:

    def handle(row: dict) -> ListDTO:
        return ListDTO([],[])