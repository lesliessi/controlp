from apscheduler.schedulers.background import BackgroundScheduler
from backup import *

def iniciar_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: respaldo_manual(app), trigger="cron", day= 1, hour=2, minute= 0)  # Cada 24h
    scheduler.start()