from __future__ import with_statement
from fabric.api import local, settings, abort, run, env, put, sudo

env.use_ssh_config = True
env.hosts = ['223.197.230.172']
#env.hosts = ['mgportfolio', '223.197.230.172']

prog_name = 'http_fs'

def deploy():
    uname = run('uname -s').lower()
    sudo('mkdir -p /opt/%s' % (prog_name, ), warn_only=True)
    sudo('mkdir -p /var/log/%s' % (prog_name, ), warn_only=True)
    sudo('chmod -R og+w /var/log/%s' % (prog_name, ))
    sudo('easy_install tornado futures')
    
    put('http_fs/*.py', '/opt/%s/' % (prog_name, ), mirror_local_mode = True, use_sudo = True)
    put('etc/*.conf', '/etc/', mirror_local_mode = True, use_sudo = True)
    put('etc/supervisor/conf.d/*.conf', '/etc/supervisor/conf.d/', mirror_local_mode = True, use_sudo = True)
    
    if 'linux' in uname:
        put('etc/logrotate.d/*', '/etc/logrotate.d/', mirror_local_mode = True, use_sudo = True)
    elif 'darwin' in uname:
        put('etc/newsyslog.d/*', '/etc/newsyslog.d/', mirror_local_mode = True, use_sudo = True)
    
    sudo('supervisorctl update')
    sudo('supervisorctl restart %s' % (prog_name, ))