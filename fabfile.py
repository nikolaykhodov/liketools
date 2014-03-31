# -*- coding: utf8 -*-
from fabric.api import sudo, run, cd, settings, put, local, env
from fabric.contrib.files import exists
import os

USER = 'liket'
HOST = 'lt.valt.me'
ADMIN_USER = 'nikolay'

env.hosts = [HOST]
env.user = USER

def test():
    """ Run tests """
    local("./manage.py test main")
    local("python run_tests.py")

def get_dirs(username):
    """ Return dict of user dirs """

    home_dir = '/home/%s/' % username
    return dict(
        home = home_dir, 
        ssh  = os.path.join(home_dir, '.ssh'), 
        http = os.path.join(home_dir, 'http'), 
        logs = os.path.join(home_dir, 'logs'), 
        env  = os.path.join(home_dir, 'http/.env')
    )


def prepare_create_user_env(username=USER, admin_user=ADMIN_USER):
    """ Create user environment """
    env.user = admin_user

    dirs = get_dirs(username)

    # install all the necessary packages
    sudo('apt-get update')
    sudo('aptitude install nginx supervisor mercurial mysql-server python-mysqldb build-essential rabbitmq-server libmysqlclient-dev python-pip python2.7-dev libevent-dev')
    sudo('pip install virtualenv')

    # add user
    with settings(warn_only=True):
        sudo('adduser %s' % username)
        sudo('adduser %s pubkey' % username)
        sudo('adduser www-data %s' % username)

        sudo('/etc/init.d/nginx restart')

    # create his directory tree
    with settings(warn_only=True):
        sudo('mkdir ' + dirs['http'])
        sudo('mkdir ' + dirs['logs'])
        sudo('mkdir ' + dirs['ssh'])

    # Root owns home dir
    sudo('chown root:root %s' % dirs['home'])
    # user owns ~/http dir
    sudo('chown %s:%s %s' % (username, username, dirs['http']))
    # both root and user own  ~/log dir, but user can't write
    sudo('chown root:%s %s' % (username, dirs['logs']))
    sudo('chmod 750 %s %s' %  (dirs['http'], dirs['logs']))

    # upload admin key
    sudo('chmod 777 %s' % dirs['ssh'])

    with cd(dirs['ssh']):
        if exists('authorized_keys'):
            sudo('unlink authorized_keys')
        put("~/.ssh/id_rsa.pub", "authorized_keys", mode=0755)
        sudo('chown root:root authorized_keys')

    sudo('chmod 755 %s' % dirs['ssh'])

def prepare_upload_code(username=USER, admin_user=ADMIN_USER):
    """ Upload code to recently created user environment """
    env.user = username

    dirs = get_dirs(username)

    # Upload code
    with cd(dirs['http']):
        if exists('.hg'):
            run('rm -rf .hg')
        run('hg init')
        local('hg push ssh://%s@%s/http --new-branch' % (username, env.host))
        run('hg up')
    
    # Create virtualenv and install PIP requirements
    run('virtualenv %s' % dirs['env'])
    run('source %s' % os.path.join(dirs['env'], 'bin/activate'))

def prepare_install_server_files(username=USER, admin_user=ADMIN_USER):
    """ Copy system files and restart daemons """
    env.user = admin_user

    dirs = get_dirs(username)

    with cd(dirs['http']):
        sudo('cp ./conf/liketools.nginx.conf      /etc/nginx/sites-enabled/')   
        sudo('cp ./conf/liketools.supervisor.conf /etc/supervisor/conf.d/')


    sudo('/etc/init.d/nginx reload')
    sudo('/etc/init.d/supervisor restart')


def prepare_server(username=USER, admin_user=ADMIN_USER):
    """ Prepare server for working """
    env.user = admin_user

    prepare_create_user_env(username)
    prepare_upload_code(username)
    update_pip(username)
    prepare_install_server_files(username)

    
def update_pip(username=None, admin_user=ADMIN_USER):
    """ Install new packages from PIP """
    if username is not None:
        env.user = username

    with cd("~/http/"):
        run(".env/bin/pip install -U -r ./pip_reqs.txt")

def deploy():
    """ Deployment """

    local("hg push ssh://liket@liketools.valt.me/http --new-branch")
    with cd("~/http/"):
        run("hg up")
        run(".env/bin/python manage.py syncdb")
        run(".env/bin/python manage.py migrate")
        run(".env/bin/python manage.py collectstatic")
        run("killall python")

