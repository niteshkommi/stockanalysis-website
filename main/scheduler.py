from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .views import Computation


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(Computation, 'cron', hour='11', minute='40')
    scheduler.start()
