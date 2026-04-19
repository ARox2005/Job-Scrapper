from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from services.tasks import refresh_company_data

scheduler = BackgroundScheduler(timezone="UTC")


def run_scheduled_refresh():
    companies = [
        company.strip()
        for company in config.SCHEDULE_REFRESH_COMPANIES.split(",")
        if company.strip()
    ]

    for company in companies:
        try:
            result = refresh_company_data(company)
            print(f"[scheduler] Refreshed {company}: {result}")
        except Exception as exc:
            print(f"[scheduler] Refresh failed for {company}: {exc}")


def start_scheduler():
    if not config.SCHEDULE_REFRESH_ENABLED or scheduler.running:
        return

    hours = [
        hour.strip()
        for hour in config.SCHEDULE_REFRESH_HOURS_UTC.split(",")
        if hour.strip()
    ]

    if not hours:
        return

    for hour in hours:
        scheduler.add_job(
            run_scheduled_refresh,
            CronTrigger(hour=int(hour), minute=0),
            id=f"refresh_{hour}",
            replace_existing=True,
        )

    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
