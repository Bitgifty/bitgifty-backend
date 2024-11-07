import threading
import time

from django.db.models import Q

from schedule import Scheduler

from .models import Transaction


def check_transaction_status():
    transactions = Transaction.objects.filter(
        Q(status="pending") | Q(status="sent")
    )
    for transaction in transactions:
        try:
            transaction.check_trans_status()
        except Exception:
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
    # scheduler.every(60).seconds.do(check_transaction_status)
    scheduler.run_continuously()
