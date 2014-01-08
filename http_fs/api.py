'''
Created on Dec 26, 2013

@author: maxim
'''
import tornado.web
import os
import datetime
import mimetypes
import email.utils
import time
import logging
    
class FileResource(tornado.web.RequestHandler):
    def initialize(self, file_dir, file_ttl_sec):
        self.file_dir = file_dir
        self.file_ttl_sec = file_ttl_sec
        self.log = logging.getLogger('file_resource')
        
    def prepare(self):
        pass
    
    def head(self, filename):
        self.get(filename, include_body=False)

    def get(self, filename, include_body=True):
        path = os.path.abspath(os.path.join(self.file_dir, filename))
        
        if not os.path.exists(path):
            raise tornado.web.HTTPError(404)
        if not os.path.isfile(path):
            raise tornado.web.HTTPError(403, "%s is not a file", path)

        modified = self._modification_date(path)

        self.set_header("Last-Modified", modified)

        mime_type, __ignore_unused_encoding = mimetypes.guess_type(path)
        if mime_type:
            self.set_header("Content-Type", mime_type)

        cache_time = self._get_cache_time(path, modified, mime_type)

        if cache_time > 0:
            self.set_header("Expires", datetime.datetime.utcnow() +
                            datetime.timedelta(seconds=cache_time))
            self.set_header("Cache-Control", "max-age=" + str(cache_time))

        # Check the If-Modified-Since, and don't send the result if the
        # content has not been modified
        ims_value = self.request.headers.get("If-Modified-Since")
        if ims_value is not None:
            date_tuple = email.utils.parsedate(ims_value)
            if_since = datetime.datetime.fromtimestamp(time.mktime(date_tuple))
            if if_since >= modified:
                self.set_status(304)
                return

        self.log.info('Returning path [%s]' % path)
        with open(path, "rb") as f:
            data = f.read()
            if include_body:
                self.write(data)
            else:
                assert self.request.method == "HEAD"
                self.set_header("Content-Length", len(data))
                
        # touch file
        os.utime(path, None)
    
    def post(self, filename):
        path = os.path.abspath(os.path.join(self.file_dir, filename))
        for fileinfo in self.request.files.itervalues():
            for http_file in fileinfo:
                #self.log.info("fileinfo is %r" % (fileinfo, ))
                self.log.info('Uploading at file path [%s] with body size %d' % (path, len(http_file['body']), ))
            
                with open(path, 'wb') as out:
                    out.write(http_file['body'])
                    
                break
            break
    
    def delete(self, filename):
        path = os.path.abspath(os.path.join(self.file_dir, filename))
        if not os.path.exists(path):
            raise tornado.web.HTTPError(404)
        if not os.path.isfile(path):
            raise tornado.web.HTTPError(403, "%s is not a file", path)
        
        self.log.info('Deleting file path [%s]' % path)
        
        os.remove(path)
    
    def _get_cache_time(self, path, modified, mime_type):
        """Override to customize cache control behavior.

        Return a positive number of seconds to make the result
        cacheable for that amount of time or 0 to mark resource as
        cacheable for an unspecified amount of time (subject to
        browser heuristics).

        By default returns cache expiry of 10 years for resources requested
        with ``v`` argument.
        """
        return self.file_ttl_sec if "v" in self.request.arguments else 0
    
    def _modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)