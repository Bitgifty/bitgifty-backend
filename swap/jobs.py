from schedule import Scheduler
import threading
import time
import requests
import json

def get_rate():
    result = {}
    coins = {
        "bitcoin": "BTC",
        "bnb": "BNB",
        "celo": "CELO",
        "ethereum": "ETH",
        "tron": "TRX",
    }

    for key in coins:
        request = requests.get(f"https://api.binance.com/api/v3/avgPrice?symbol={coins[key]}USDT")
        data = request.json()
        result[key] = data["price"]
    
    with open('price.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    

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
    scheduler.every(5).minutes.do(get_rate)
    scheduler.run_continuously()