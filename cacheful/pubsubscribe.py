"""
This file allows the user to subscribe to different levels of events that
happen within the timechecker module.
"""
import logging


class Publisher(object):
    """
    Class that handles the subscription and publishing of notifications
    related to the timechecker module.
    """

    def __init__(self):
        self.subscribers = []
        self.levels = {'INFO': 1, 'EVENT': 2, 'WARNING': 3, 'ERROR': 4,
                       'EXCEPTION': 4}

    def subscribe(self, subscription, level='EVENT'):
        """
        Subscribe to the publisher. Argument 'subscription' should be a class
        that has a method 'notify' that takes a dictionary called 'notedict'
        and a string 'notestring'.

        Specify the lowest level of event that necesitates a notification
        chooseing from 'INFO', 'EVENT', 'WARNING', 'ERROR', and 'EXCEPTION'.
        For example, if you choose 'WARNING', you will recieve notifications
        for 'WARNING', 'ERROR', and 'EXCEPTION'. This defaults to 'EVENT'.
        """
        if level not in self.levels.keys():
            level = 'EVENT'
        self.subscribers.append({'subscriber': subscription, 'level': level})

    def publish(self, level, data):
        """
        Publishes a notification to all subscribers that have selected the
        notification's event-level or lower.
        """
        for subscriber in self.subscribers:
            if (self.levels[subscriber['level']] <= self.levels[level]):
                notedict = self.makenotification(level, data)
                notestring = self.buildnotestring(notedict)
                subscriber['subscriber'].notify(notedict=notedict,
                                                notestring=notestring)

    def makenotification(self, level, data):
        """
        Builds the dictionary of the notification.
        """
        message = str(data['message'])
        details = data['details']
        return {'level': level, 'message': message, 'details': details}

    def buildnotestring(self, notification):
        """
        Builds the string representation of the notification dictionary.
        """
        note = 'Level: {}'.format(notification['level'])
        note += '; Message: "{}"'.format(notification['message'])
        if len(notification['details']) > 0:
            klist = list(notification['details'].keys())
            note += '; Details: '
            for key in klist[:-1]:
                note += '{}: {}, '.format(str(key),
                                          str(notification['details'][key]))
            lkey = klist[len(klist) - 1]
            note += '{}: {}'.format(str(lkey),
                                    str(notification['details'][lkey]))
        else:
            note += '; Details: None'
        return note


class LoggingHandler(object):
    """
    Class to serve as a basic system for logging published notifications.
    """

    def notify(self, notedict, notestring):
        """
        Required method name and parameters for a subscriber. Simply logs the
        notification.
        """
        logging.info(notestring)
