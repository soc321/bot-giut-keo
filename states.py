from aiogram.fsm.state import StatesGroup, State

class DepositState(StatesGroup):
    amount = State()

class WithdrawState(StatesGroup):
    amount = State()
