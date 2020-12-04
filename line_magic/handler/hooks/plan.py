from functools import wraps
import schedule
import time


class ScheduleHooks(object):
    def __init__(self, schedule_funcs):
        '''Register funcs'''
        for f in schedule_funcs:
            if hasattr(f, 'minutely'):
                schedule.every().minute.do(f, self)
            elif hasattr(f, 'hourly'):
                schedule.every().hour.do(f, self)
            elif hasattr(f, 'daily'):
                schedule.every().day.do(f, self)
            elif hasattr(f, 'weekly'):
                schedule.every().week.do(f, self)
            elif hasattr(f, 'monthly'):
                schedule.every().month.do(f, self)

    def schedule_thread(self):
        '''Execute Schedule Functions (Thread)'''
        while True:
            schedule.run_pending()
            time.sleep(1)

    def Minutely(self):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 3
            func.Schedule = True
            func.minutely = True

            @wraps(func)
            def __sc(self, *args, **kwargs):
                func(args[0], args[0].cl)
            return __sc
        return __wrapper

    def Hourly(self):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 3
            func.Schedule = True
            func.hourly = True

            @wraps(func)
            def __sc(self, *args, **kwargs):
                func(args[0], args[0].cl)
            return __sc
        return __wrapper

    def Daily(self):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 3
            func.Schedule = True
            func.daily = True

            @wraps(func)
            def __sc(self, *args, **kwargs):
                func(args[0], args[0].cl)
            return __sc
        return __wrapper

    def Weekly(self):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 3
            func.Schedule = True
            func.weekly = True

            @wraps(func)
            def __sc(self, *args, **kwargs):
                func(args[0], args[0].cl)
            return __sc
        return __wrapper

    def Monthly(self):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 3
            func.Schedule = True
            func.monthly = True

            @wraps(func)
            def __sc(self, *args, **kwargs):
                func(args[0])
            return __sc
        return __wrapper
