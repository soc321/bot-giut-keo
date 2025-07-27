from aiogram.fsm.state import State, StatesGroup

class DepositState(StatesGroup):
    amount = State()

class WithdrawState(StatesGroup):
    amount = State()

class BankInfoState(StatesGroup):
    bank = State()
    account = State()
    name = State()
