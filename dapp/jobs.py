import threading
import time
import os

from django.db.models import Q

from schedule import Scheduler

from dapp.models import Transaction
from wallets.models import Wallet


def check_flw_trans_dapp():
    if os.environ['DEBUG'] == 'True':
        return

    if os.environ['FROZEN'] == 'True':
        return

    transactions = Transaction.objects.filter(
        Q(status="pending") | Q(status="sent")
    )
    for transaction in transactions:
        if len(transaction.wallet_address) > 1:
            try:
                transaction.check_flw_tran()
            except Exception as exception:
                print("exception while processing: ", exception)
                continue


def stellar_job():
    if os.environ['DEBUG'] == 'True':
        return

    if os.environ['FROZEN'] == 'True':
        return

    wallets = Wallet.objects.filter(chain="stellar")

    for wallet in wallets:
        try:
            wallet.top_xlm()
        except Exception as exception:
            print("exception while processing: ", exception)
            continue


def run_continuously(self, interval=1):
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour then your job won't be run 60 times at each interval but
    only once.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously


def start_scheduler():
    scheduler = Scheduler()
    scheduler.run_continuously()
