"""
The timechecker module is used to schedule functions without requiring the
operating system to do so.

The method timer accepts several parameters that specify when the function
(which, along with its parameters, is passed to timer) will be run.

Using a file whose name defaults to 'timer.pid', the timechecker module
knows not to begin timing in multiple processes. Think of a server which is
running multiple instances of an application that only one of which needs to
download a file one an hour.

Timechecker uses a publisher-subscriber model so the user can see as much or
as little logging info as they desire. See the pubsubscribe module for more.
"""
from __future__ import print_function
import os
import os.path
import time
import datetime
from atexit import register
import threading
import logging
from pubsubscribe import Publisher, LoggingHandler


def timer(FUNCTION, PARAMS, UPDATE_TIME, UPDATE_PERIOD,
          UPDATE_PID_NAME='timer.pid', PUBLISHER=None):
    """
    Starts the timer if it is valid to do so.

    FUNCTION and PARAMS are the variables that represent the action that needs
    to be taken at the scheduled times. These are required. FUNCTION must be a
    callable function and PARAMS must be a tuple.

    UPDATE_TIME and UPDATE_PERIOD are required variables where UPDATE_TIME
    is the first time the event should happen and UPDATE_PERIOD is the length
    of time between each event.

    UPDATE_PID_NAME is the name of the file that ensures that only one
    timechecker process is running at a time. It defaults to 'timer.pid'.

    PUBLISHER is a pubsubscribe.Publisher object (or None) that will default
    to a publisher with no subscribers if it is not specified. See the
    pubsubscribe module for details.
    """
    function = FUNCTION
    if not hasattr(function, '__call__'):
        raise TypeError('FUNCTION must be a callable function.')
    params = tuple(PARAMS)
    publisher = PUBLISHER
    if not publisher:
        publisher = Publisher()
    if type(publisher) is not Publisher:
        raise TypeError('PUBLISHER must be of type Publisher.')

    @register
    def removeupdatepid():
        """
        Deletes the pid file and logs it upon exit from the process.
        """
        try:
            fname = UPDATE_PID_NAME
            with open(fname, 'r') as f:
                content = f.readlines()
            if len(content) > 0 and content[0] == str(os.getpid()):
                os.remove(fname)
                publisher.publish('EVENT', {'message': 'Stopping timer' +
                                            ' and deleting file.',
                                            'details': {'filename': fname}})
            else:
                publisher.publish('EVENT', {'message': 'Did not remove file.',
                                            'details': {'filename': fname}})
        except:
            publisher.publish('WARNING', {'message': 'Could not remove file.',
                                          'details': {'filename':
                                                      UPDATE_PID_NAME}})

    try:
        utime = _checktimevar(UPDATE_TIME)
        period = _checkperiodvar(UPDATE_PERIOD)
    except ValueError as e:
        publisher.publish('EXCEPTION', {'message': 'ValueError',
                                        'details': {'exception': e}})
        raise

    try:
        fname = UPDATE_PID_NAME
        if _nonerunning(fname):
            publisher.publish('EVENT', {'message': 'Starting timer and' +
                                        ' opening the tracking file.',
                                        'details': {'filename': fname}})
            with open(fname, 'w') as f:
                f.write(str(os.getpid()))
                _timechecker(function, params, publisher, utime, period)
        else:
            raise OSError('Timer already in process.')
    except OSError as e:
        publisher.publish('EXCEPTION', {'message': 'OSError',
                                        'details': {'exception': e}})
    except Exception as e:
        publisher.publish('EXCEPTION', {'message': 'Unexpected Exception',
                                        'details': {'exception': e}})
    raise


def _checktimevar(UPDATE_TIME):
    time.strptime(UPDATE_TIME, '%H:%M:%S')
    return UPDATE_TIME


def _checkperiodvar(UPDATE_PERIOD):
    time.strptime(UPDATE_PERIOD, '%H:%M:%S')
    period = _periodtoseconds(UPDATE_PERIOD)
    if period < 120:
        raise ValueError('The minimum UPDATE_PERIOD is 2 minutes ' +
                         '(120 seconds), not {}'.format(UPDATE_PERIOD))
    return period


def _nonerunning(fname):
    return not os.path.isfile(fname)


def _timechecker(function, params, publisher, utime, period):
    t = threading.Thread(target=_checker, args=(function, params, publisher,
                                                utime, period))
    t.daemon = True
    t.start()
    while True:
        try:
            time.sleep(100)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            time.sleep(100)


def _checker(function, params, publisher, utime, period):
    starttime = _makestart(utime, period)
    publisher.publish('EVENT', {'message': 'Timer info validated and timer' +
                                ' started.',
                                'details': {'starttime': starttime,
                                            'period': '{} seconds'
                                            .format(period)}})
    while True:
        try:
            now = datetime.datetime.now()
            starttime += _checktime(function, params, publisher, now,
                                    starttime, period)
            time.sleep(int(period / 100))
        except Exception as e:
            publisher.publish('EXCEPTION', {'message': 'Unexpected Exception',
                                            'details': {'exception': e}})
            time.sleep(int(period / 100))


def _makestart(utime, period):
    """
    If update time is in the past, it adds consecutive periods until the new
    starttime is in the future.
    """
    parts = utime.split(':')
    hour = int(parts[0])
    minute = int(parts[1])
    second = int(parts[2])

    now = datetime.datetime.now()
    starttime = now.replace(hour=hour, minute=minute, second=second,
                            microsecond=0)
    while now > starttime:
        starttime += datetime.timedelta(seconds=period)
    return starttime


def _checktime(function, params, publisher, now, starttime, period):
    endtime = starttime + datetime.timedelta(seconds=(int(period / 20)))
    publisher.publish('INFO', {'message': 'Checking time.',
                               'details': {'time': now}})
    if starttime < now < endtime:
        try:
            _runfunction(function, params, publisher)
            return datetime.timedelta(seconds=period)
        except Exception as e:
            publisher.publish('EXCEPTION', {'message': 'Unexpected Exception',
                                            'details': {'exception': e}})
            return datetime.timedelta(seconds=0)
    else:
        return datetime.timedelta(seconds=0)


def _runfunction(function, params, publisher):
    """
    Runs the function passed to timechecker witht he associated params and
    times it.
    """
    publisher.publish('EVENT', {'message': 'It is time for the action.',
                                'details': {'function': str(function),
                                            'params': str(params)}})
    t = time.time()
    function(*params)
    elapsed = str(time.time() - t) + ' seconds'
    publisher.publish('EVENT', {'message': 'Action completed.',
                                'details': {'timeelapsed': elapsed}})


def _periodtoseconds(pstring):
    parts = pstring.split(':')
    hour = int(parts[0])
    minute = int(parts[1])
    second = int(parts[2])
    total = second + (60 * minute) + (60 * 60 * hour)
    return int(total)


if __name__ == '__main__':
    from os.path import join, dirname
    from dotenv import load_dotenv
    ENVFILE_PATH = join(dirname(__file__), '..', '.env')
    load_dotenv(ENVFILE_PATH)
    logging.basicConfig(level=logging.INFO)

    publisher = Publisher()
    publisher.subscribe(LoggingHandler(), level='INFO')
    publisher.publish('INFO', {'message': 'Timer called from main.',
                               'details': {}})
    timer(print, ('It\'s happening', 'now!'), os.environ['UPDATE_TIME'],
          os.environ['UPDATE_PERIOD'], os.environ['UPDATE_PID_NAME'],
          publisher)
