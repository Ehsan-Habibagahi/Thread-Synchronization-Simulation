from BankAccount import BankAccount
from utils import ReentrantMutex


class BankingSystem:

    def __init__(self, num_accounts=10):
        self.accounts = {}
        for i in range(num_accounts):
            self.accounts[i] = BankAccount(i, initial_balance=1000)

    def deposit(self, account_id, amount):
        return self.accounts[account_id].deposit(amount)

    def withdraw(self, account_id, amount):
        return self.accounts[account_id].withdraw(amount)

    def get_balance(self, account_id):
        return self.accounts[account_id].get_balance()

    def get_total_money(self):
        with self.mutex:
            total = 0
            for account in self.accounts.values():
                total += account.get_balance()
            return total

