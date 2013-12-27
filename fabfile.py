from __future__ import with_statement
from fabric.api import local, settings, abort, run, env, put, sudo

env.use_ssh_config = True
env.hosts = ['223.197.230.172']
#env.hosts = ['mgportfolio', '223.197.230.172']

def deploy():
    uname = run('uname -s').lower()
    sudo('mkdir -p /opt/http_fs', warn_only=True)
    sudo('mkdir /var/log/http_fs', warn_only=True)
    sudo('chmod -R og+w /var/log/http_fs')
    sudo('easy_install tornado futures')
    
    put('http_fs/*.py', '/opt/http_fs/', mirror_local_mode = True, use_sudo = True)
    put('http_fs/*.xml', '/opt/http_fs/', mirror_local_mode = True, use_sudo = True)
    put('etc/*.conf', '/etc/', mirror_local_mode = True, use_sudo = True)
    put('etc/supervisor/conf.d/*.conf', '/etc/supervisor/conf.d/', mirror_local_mode = True, use_sudo = True)
    
    if 'linux' in uname:
        put('etc/logrotate.d/http_fs', '/etc/logrotate.d/http_fs', mirror_local_mode = True, use_sudo = True)
    elif 'darwin' in uname:
        put('etc/newsyslog.d/eu.mgportfolio.http_fs.conf', '/etc/newsyslog.d/eu.mgportfolio.http_fs.conf', mirror_local_mode = True, use_sudo = True)
    
    sudo('supervisorctl update')
    sudo('supervisorctl restart http_fs')