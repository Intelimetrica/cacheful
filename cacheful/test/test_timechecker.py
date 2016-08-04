"""
Test file for the timechecker module.
"""
import cacheful.timechecker as timechecker
from cacheful.pubsubscribe import Publisher
import os
import time
import datetime
from multiprocessing import Process
import pytest


def printfull(first, last):
    print first, last


def printfirst(first):
    print first, 'Nolast'


def test_periodtoseconds():

    # Random valid value
    assert(timechecker._checkperiodvar('8:37:26') == 31046)

    # Minimum value
    assert(timechecker._checkperiodvar('00:02:00') == 120)

    # Too small
    with pytest.raises(ValueError):
        timechecker._checkperiodvar('0:1:59')


def test_checktime():

    func = printfull
    params = ('John', 'Smith')

    publisher = Publisher()

    now = datetime.datetime.now()
    starttime = now - datetime.timedelta(seconds=1)
    period = 120

    # It is time, so should return a timedelta of 120 seconds
    now = datetime.datetime.now()
    newstart1 = starttime + timechecker._checktime(func, params, publisher,
                                                   now, starttime, period)
    assert(starttime + datetime.timedelta(seconds=period) == newstart1)

    # Not yet time, so should return a timedelta of 0 seconds
    now = datetime.datetime.now() + datetime.timedelta(seconds=1)
    newstart2 = newstart1 + \
        timechecker._checktime(func, params, publisher, now, newstart1, period)
    assert(newstart1 + datetime.timedelta(seconds=0) == newstart2)

    # Figuratively added 120 seconds to current time, so it it time again
    now = datetime.datetime.now() + datetime.timedelta(seconds=period)
    newstart3 = newstart2 + \
        timechecker._checktime(func, params, publisher, now, newstart2, period)
    assert(newstart2 + datetime.timedelta(seconds=period) == newstart3)


def test_makestart():

    # Update time is in the future of the day so it should not change
    now = datetime.datetime.now()
    period = 180
    update = now + datetime.timedelta(seconds=3600)
    update = update.replace(microsecond=0)
    utime = '{}:{}:{}'.format(str(update.hour), str(update.minute),
                              str(update.second))
    assert(update == timechecker._makestart(utime, period))

    # Update time is in the past of the day and should increase by one period
    now = datetime.datetime.now()
    period = 3600
    update = now - datetime.timedelta(seconds=1000)
    update = update.replace(microsecond=0)
    utime = '{}:{}:{}'.format(str(update.hour), str(update.minute),
                              str(update.second))
    assert(update + datetime.timedelta(seconds=3600) ==
           timechecker._makestart(utime, period))

    # Update time is way in the past of the day and should increase by six
    # periods
    now = datetime.datetime.now()
    period = 3600
    update = now - datetime.timedelta(seconds=20000)
    update = update.replace(microsecond=0)
    utime = '{}:{}:{}'.format(str(update.hour), str(update.minute),
                              str(update.second))
    assert(update + datetime.timedelta(seconds=(3600 * 6)) ==
           timechecker._makestart(utime, period))


def test_timer():

    func = printfirst
    params = 'Jane'

    publisher = Publisher()
    fname = 'update.pid'
    args = [func, params, '11:11:30', '00:03:00', fname, publisher]

    # None started so should be True
    assert(timechecker._nonerunning(fname))

    p1 = Process(target=timechecker.timer, args=args)
    p1.daemon = True
    p1.start()
    time.sleep(0.1)

    # One already started so should be False
    assert(not timechecker._nonerunning(fname))

    p1.terminate()
    os.remove(fname)

    p2 = Process(target=timechecker.timer, args=args)
    p2.daemon = True
    p2.start()
    time.sleep(0.1)

    pfail = Process(target=timechecker.timer, args=args)
    pfail.daemon = True

    # One already started so should raise OSError
    with pytest.raises(OSError):
        pfail.run()
        pfail.terminate()

    p2.terminate()
    os.remove(fname)
