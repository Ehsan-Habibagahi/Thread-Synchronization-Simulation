import threading
import random
import time


class ATMThread(threading.Thread):
    def __init__(self, atm_id, banking_system, num_operations=20):
        super().__init__(name=f"ATM id:{atm_id}")
        self.atm_id = atm_id
        self.banking_system = banking_system
        self.num_operations = num_operations
        self.successful_ops = 0
        self.failed_ops = 0

    def run(self):
        """
        Perform random deposits and withdrawals.
        Each operation should:
        - Select random account
        - Select random amount ($10-$500)
        - Randomly choose deposit or withdrawal
        - Add small delay (0.01s) to simulate ATM processing
        """
        for i in range(self.num_operations):
            # random things
            account_id = random.randint(
                0, len(self.banking_system.accounts) - 1)
            amount = random.randint(10, 500)
            operation = random.choice(['deposit', 'withdraw'])
            try:
                if operation == 'deposit':
                    new_balance = self.banking_system.deposit(
                        account_id, amount)
                    print(
                        f"[{self.name}] Deposited ${amount} to account {account_id} = ${new_balance}")
                else:
                    new_balance = self.banking_system.withdraw(
                        account_id, amount)
                    print(
                        f"[{self.name}] Withdrew ${amount} from account {account_id} = ${new_balance}")

                self.successful_ops += 1

            except Exception as e:
                print(f"atm failure ({self.atm_id}): {e}")  # debug
                self.failed_ops += 1
            time.sleep(0.01)
