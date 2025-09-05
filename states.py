from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    HelpTopic = State()
    ReportProblem = State()
    AskQuestion = State()
    AddEvent = State()
    AddAdmin = State()
    AiChat = State()
