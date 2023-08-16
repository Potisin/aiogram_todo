from aiogram.fsm.state import StatesGroup, State


class CreatingCatalog(StatesGroup):
    request_catalog_name = State()
    created_catalog = State()


class CreatingTask(StatesGroup):
    request_task_name = State()
    request_task_description = State()
    request_task_deadline = State()
    create_task = State()
