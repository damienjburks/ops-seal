"""
DefaultScheduler Module
This module provides a DefaultScheduler class that uses APScheduler to run jobs at specified intervals.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.clients.tfc_client import TfcClient


class DefaultScheduler:
    """
    A class to schedule and run the various jobs periodically.
    """

    def __init__(self, interval_hours=24):
        """
        Initializes the CronJob Class.

        Args:
            interval_hours (int): The interval in hours at which the DefaultScheduler should run.
        """
        self.scheduler = BackgroundScheduler()
        self.interval_hours = interval_hours

    def start(self):
        """
        Starts the scheduler and schedules jobs.
        """
        logging.info("Starting scheduler...")
        self.scheduler.add_job(
            self._run_tfc_client,
            trigger=IntervalTrigger(hours=self.interval_hours),
            id="tfc_client_job",
            replace_existing=True,
        )
        self.scheduler.start()
        logging.info("Scheduler started.")
        logging.info("Scheduler will run every %d hours.", self.interval_hours)

    def _run_tfc_client(self):
        """
        Initializes and runs the TfcClient.
        """
        logging.info("Starting TfcClient...")
        try:
            TfcClient().run()
            logging.info("TfcClient run completed successfully.")
        except RuntimeError as e:  # Replace with a more specific exception if applicable
            logging.error("Error running TfcClient: %s", e)