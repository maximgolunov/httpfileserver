'''
Created on Dec 26, 2013

@author: maxim
'''
import logging
import os
import datetime
import tornado.ioloop

class task(object):
    def __init__(self, file_dir, file_ttl_sec):
        self.file_dir = file_dir
        self.file_ttl_sec = file_ttl_sec
        self.log = logging.getLogger('housekeeping')
        
    def start(self, ioloop):
        self.callback = tornado.ioloop.PeriodicCallback(self.cleanup, (1000 * self.file_ttl_sec) / 10, ioloop)
        self.log.info('Housekeeper scheduled to run every %d sec' % (self.file_ttl_sec / 10, ))
        self.callback.start()
        
    def stop(self):
        self.callback.stop()
        
    def cleanup(self):
        if not os.path.exists(self.file_dir):
            return
            
        self.log.debug('Running cleanup task in directory %s...' % (self.file_dir, ))
        
        threshold_date = datetime.datetime.now() - datetime.timedelta(seconds = self.file_ttl_sec)
        
        for f in os.listdir(self.file_dir):
            filepath = os.path.join(self.file_dir, f)
            if os.path.isfile(filepath):
                mod_date = self._modification_date(filepath)
                if mod_date < threshold_date:
                    self.log.info('File [%s] was last accessed longer than %d seconds ago, removing.' % (f, self.file_ttl_sec,))
                    os.remove(filepath)
        
        self.log.debug('Cleanup done.')
    
    def _modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)