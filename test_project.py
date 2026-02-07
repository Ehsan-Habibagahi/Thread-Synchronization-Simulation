import threading
import time
import random
from utils import CountingSemaphore
from utils import ReentrantMutex
from BankingSystem import BankingSystem
from BankAccount import BankAccount
from ATMThread import ATMThread


def test_semaphore_basic():
    """Test that semaphore correctly limits resource access"""
    print("\n" + "=" * 50)
    print("TEST: Semaphore Basic")
    print("=" * 50)

    semaphore = CountingSemaphore(2)
    concurrent_count = [0]
    max_concurrent = [0]
    results = []
    lock = threading.Lock()

    def helper(helper_id):
        if semaphore.acquire(timeout=3):
            try:
                with lock:
                    concurrent_count[0] += 1
                    if concurrent_count[0] > max_concurrent[0]:
                        max_concurrent[0] = concurrent_count[0]
                    results.append(
                        f"helper {helper_id} acquired (concurrent: {concurrent_count[0]})")
                with lock:
                    concurrent_count[0] -= 1
                    results.append(
                        f"helper {helper_id} released (concurrent: {concurrent_count[0]})")
            finally:
                semaphore.release()
        else:
            results.append(f"helper {helper_id} timedout")

    # The job of 5 threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=helper, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for result in results:
        print(result)

    print(f"Max concurrent slut: {max_concurrent[0]}")
    if max_concurrent[0] == 2:
        print(f"PASS: semaphore correctly limited to 2 sluts")
    else:
        print(f"FAIL: expect: 2, got {max_concurrent[0]}")

    return max_concurrent[0] == 2


def test_mutex_ownership():
    """Test that mutex correctly tracks ownership"""
    print("\n" + "=" * 50)
    print("TEST: Mutex Ownership")
    print("=" * 50)
    mutex = ReentrantMutex()
    results = []
    print("\nTest: Reentrant acquisition")
    mutex.acquire()
    print("*1 acquire successful")
    mutex.acquire()
    print("*2 acquire successful (reentrant)")
    mutex.acquire()
    print("*3 acquire successful (reentrant)")
    mutex.release()
    print("*1 release successful")
    mutex.release()
    print("*2 release successful")
    mutex.release()
    print("*3 release successful")
    print("PASS: was reentrant")

    print("\nTest: Different thread cant release")
    mutex.acquire()
    release_failed = [False]

    def try_release():
        try:
            mutex.release()
            print("FAIL: Other thread released mutex")
        except RuntimeError as e:
            print(f"PASS: Didn't release")
            release_failed[0] = True

    other_thread = threading.Thread(target=try_release)
    other_thread.start()
    other_thread.join()

    mutex.release()
    print("Main thread released mutex")

    if release_failed[0]:
        print("\nPASS: Different thread cant release mutex")
        return True
    else:
        print("\nFAIL: Different thread could release mutex")
        return False


def test_concurrent_deposits():
    """Test that concurrent deposits don't lose money"""
    print("\n" + "=" * 50)
    print("TEST 3: Concurrent Deposits")
    print("=" * 50)

    account = BankAccount(0, initial_balance=1000)
    num_threads = 10
    deposit_amount = 100

    def depositor(thread_id):
        account.deposit(deposit_amount)
        print(f"Thread {thread_id} deposited ${deposit_amount}")

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=depositor, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    expected_balance = 1000 + (num_threads * deposit_amount)
    final_balance = account.get_balance()

    print(f"\nExpected: ${expected_balance}")
    print(f"Acual:    ${final_balance}")

    if final_balance == expected_balance:
        print("PASS: All deposits completed")
        return True
    else:
        print(f"FAIL: Lost ${expected_balance - final_balance}")
        return False


def test_concurrent_withdrawals():
    """Test that concurrent withdrawals don't create negative balance"""
    print("\n" + "=" * 50)
    print("TEST 4: Concurrent Withdrawals")
    print("=" * 50)
    account = BankAccount(0, initial_balance=1000)
    num_threads = 20
    withdrawal_amount = 100
    successful_withdrawals = [0]
    failed_withdrawals = [0]
    lock = threading.Lock()

    def withdrawer(thread_id):
        try:
            account.withdraw(withdrawal_amount)
            with lock:
                successful_withdrawals[0] += 1
            print(f"Thread {thread_id} withdrew ${withdrawal_amount}")
        except Exception as e:
            with lock:
                failed_withdrawals[0] += 1
            print(f"Thread {thread_id} failed (insufficient funds)")

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=withdrawer, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    final_balance = account.get_balance()
    expected_balance = 1000 - (successful_withdrawals[0] * withdrawal_amount)
    print(f"\nSuccessful withdrawals: {successful_withdrawals[0]}")
    print(f"Failed withdrawals: {failed_withdrawals[0]}")
    print(f"Expected balance: {expected_balance}")
    print(f"Final balance: {final_balance}")

    if final_balance >= 0 and final_balance == expected_balance:
        print("PASS: Correct balance")
        return True
    elif final_balance < 0:
        print(f"FAIL: Negative balance: ${final_balance}")
        return False
    else:
        print(f"FAIL: Balance mismatch")
        return False


def test_system_integrity():
    """Test that total money in system remains constant"""
    print("\n" + "=" * 50)
    print("TEST 5: System Integrity")
    print("=" * 50)

    banking_system = BankingSystem(num_accounts=10)
    initial_total = banking_system.get_total_money()
    print(f"Initial total money: ${initial_total}")
    num_atms = 3
    operations_per_atm = 100

    print(f"\nStart ATM threads")

    threads = []
    for i in range(num_atms):
        atm = ATMThread(i, banking_system, num_operations=operations_per_atm)
        threads.append(atm)
        atm.start()

    for atm in threads:
        atm.join()

    final_total = banking_system.get_total_money()

    print(f"\nFinal total money: ${final_total}")
    print(f"Difference: {final_total - initial_total}")
    #########################################################################

    # Debug area

    final_total = banking_system.get_total_money()

    print("\nVerifying trans")
    for account_id, account in banking_system.accounts.items():
        deposits = sum(amt for op, amt, _,
                       _ in account.trans_log if op == 'deposit')
        withdrawals = sum(amt for op, amt, _,
                          _ in account.trans_log if op == 'withdraw')
        expected = 1000 + deposits - withdrawals
        actual = account.balance

        if expected != actual:
            print(
                f"Account {account_id}: expected ${expected}, actual: ${actual}")
            print(f"Deposits: ${deposits}, withdrawals: ${withdrawals}")
        else:
            print(f"correct")

    ##########################################################################
    # Print stats
    total_successful = sum(atm.successful_ops for atm in threads)
    total_failed = sum(atm.failed_ops for atm in threads)

    print(f"\nTotal operations:")
    print(f"Successful: {total_successful}")
    print(f"Failed: {total_failed}")

    for atm in threads:
        print(f"{atm.name}: {atm.successful_ops} successful, {atm.failed_ops} failed")

    if final_total == initial_total:
        print("\nPASS: Total money in system remained constant")
        return True
    else:
        print(f"\nFAIL: Money changed by ${final_total - initial_total}")
        return False


if __name__ == "main":
    print("=" * 60)
    print("Run")
    print("=" * 60)

    tests = [
        ("Semaphore Basic", test_semaphore_basic),
        ("Mutex Ownership", test_mutex_ownership),
        ("Concurrent Deposits", test_concurrent_deposits),
        ("Concurrent Withdrawals", test_concurrent_withdrawals),
        ("System Integrity", test_system_integrity),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nEXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")
    print(f"\n{total - passed} test(s) failed")

