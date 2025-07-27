from aiogram.fsm.state import State, StatesGroup

class InvestmentStates(StatesGroup):
    choosing_package = State()

class DepositStates(StatesGroup):
    entering_amount = State()

class WithdrawStates(StatesGroup):
    entering_amount = State()
