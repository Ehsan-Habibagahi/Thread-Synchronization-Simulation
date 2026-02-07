import threading
import time
import random
from utils import CountingSemaphore
from utils import ReentrantMutex


class BankAccount:

    def __init__(self, account_id, initial_balance=1000):
        self.account_id = account_id
        self.balance = initial_balance
        self.mutex = ReentrantMutex()
        self.trans_log = []

    def deposit(self, amount):
        "Return : balance after deposit"
        if amount<=0:
            raise ValueError("Deposite should be positive")
        # I did CMP to use it here easier!
        with self.mutex:
            old_balance = self.balance
            self.balance += amount
            self.trans_log.append(('deposit', amount, old_balance, self.balance))
            # new_balance = self.balance
            return self.balance
    def withdraw(self, amount):
        "Return : balance after deposit"
        if amount <=0:
            raise ValueError("Deposite should be positive")
        
        with self.mutex:
            if self.balance < amount:
                self.trans_log.append(('faild withraw', amount, self.balance, self.balance))
                raise Exception("insufficient funds")
            old_balance = self.balance
            self.balance -=amount
            self.trans_log.append(('withdraw', amount, old_balance, self.balance))
            # new_balance = self.balance
            return self.balance
    def get_balance(self):
        with self.mutex:
            return self.balance
        