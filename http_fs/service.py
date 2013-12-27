'''
Created on May 14, 2013

@author: maxim
'''

import os
import sys
import errno
import tornado.web
from tornado.options import options
import logging
import api
import housekeeping

options.define("config", type=str, help="Path to config file",
       callback=lambda path: options.parse_config_file(path, final=False))

options.define("http_port", default = 9090, help = "API port", type = int)
options.define("file_dir", help = "Base directory for file storage", type = str)
options.define("file_ttl_sec", default = 3600, help = "File TTL since last access in seconds", type = int)

def ensure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

if __name__ == "__main__":
    options.parse_command_line()
    
    required_keys = ('file_dir',)
    
    missing_required = None        
    for k in required_keys:
        if options.__getattr__(k) is None:
            missing_required = k 
            break

    if missing_required is not None:
        print 'Missing required parameter: %s\n' % (missing_required)
        options.print_help()
        sys.exit()

    # prepare directory        
    ensure_path_exists(options.file_dir)
    
    log = logging.getLogger('service')
    log.info('Starting service on port %d...' % (options.http_port, ))
    
    application = tornado.web.Application([
                                           (r"/log/(.*)", tornado.web.StaticFileHandler, 
                                            {'path' : os.path.dirname(options.log_file_prefix), 
                                             'default_filename' : os.path.basename(options.log_file_prefix)
                                            }),
                                           
                                           (r"/api/v1/files/([^/]+)", api.FileResource, 
                                            {'file_dir' : options.file_dir, 
                                             'file_ttl_sec' : int(options.file_ttl_sec)}),
                                           ])

    application.listen(options.http_port)
    
    ioloop = tornado.ioloop.IOLoop.instance()
    
    housekeeping_task = housekeeping.task(options.file_dir, int(options.file_ttl_sec))
    housekeeping_task.start(ioloop)
    
    ioloop.start()
