import logging
from datetime import datetime, timedelta
import traceback

from django_cron.models import CronJobLog, CronTimer


class BaseSchedule(object):
    """
    Sub classes should have the following methods:
    + should_run_now(self, cron_job) - return True if the cron job should run based on the schedule. False otherwise.
    """
    pass
    
class Schedule(BaseSchedule):
    def __init__(self, run_every_mins=60):
        self.run_every_mins = run_every_mins
        
    def should_run_now(self, cron_job):
        qset = CronJobLog.objects.filter(code=cron_job.code, is_success=True).order_by('-start_time')
        if qset:
            previously_ran_successful_cron = qset[0]
            if datetime.now() < previously_ran_successful_cron.start_time + timedelta(minutes=self.run_every_mins):
                return False
    
        return True

class DeferedCronSchedule(BaseSchedule):
    def __init__(self, run_every_mins=60):
        self.run_every_mins = run_every_mins
    
    def should_run_now(self, cron_job):
        timer, created = CronTimer.objects.get_or_create(code=cron_job.code)
        if created:
            # check log
            qset = CronJobLog.objects.filter(code=cron_job.code, is_success=True).order_by('-start_time')
            if qset:
                previously_ran_successful_cron = qset[0]
                timer.next_run_time = previously_ran_successful_cron.start_time + timedelta(minutes=self.run_every_mins)
            else:
                timer.next_run_time = datetime.now()
            timer.save()
        
        if datetime.now() > timer.next_run_time:
            return True
        
        return False
        
    def defer(self, cron_job):
        """
        Defers the cron job to not run for self.run_every_mins from now.  Resets the timer.
        """
        timer, created = CronTimer.objects.get_or_create(code=cron_job.code)
        timer.next_run_time = datetime.now() + timedelta(minutes=self.run_every_mins)
        timer.save()
        
class CronJobBase(object):
    """
    Sub-classes should have the following properties:
    + code - This should be a code specific to the cron being run. Eg. 'general.stats' etc.
    + schedule
    
    Following functions:
    + do - This is the actual business logic to be run at the given schedule
    """
    pass

class CronJobManager(object):
    """
    A manager instance should be created per cron job to be run. Does all the logging tracking etc. for it.
    """
    
    @classmethod
    def __should_run_now(self, cron_job):
        """
        Returns a boolean determining whether this cron should run now or not!
        """
        return cron_job.schedule.should_run_now(cron_job)
    
    @classmethod
    def run(self, cron_job):
        """
        apply the logic of the schedule and call do() on the CronJobBase class
        """
        if not isinstance(cron_job, CronJobBase):
            raise Exception, 'The cron_job to be run should be a subclass of %s' % CronJobBase.__class__
        
        if CronJobManager.__should_run_now(cron_job):
            logging.info("Running cron: %s" % cron_job)
            cron_log = CronJobLog(code=cron_job.code, start_time=datetime.now())
            
            try:
                cron_job.do()
                cron_log.is_success = True
            except Exception, e:
                cron_log.is_success = False
                cron_log.message = traceback.format_exc()[-1000:]
            
            cron_log.end_time = datetime.now()
            cron_log.save()
