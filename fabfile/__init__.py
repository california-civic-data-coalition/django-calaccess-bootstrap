from __future__ import with_statement

import yaml
import time
from fabric.colors import green
from fabric.api import env, local, task

from amazon import createserver, createrds, clonerds
from configure import configure
from configure import ConfigTask
from chef import installchef, cook
from app import restartapache, rmpyc
from app import pipinstall, manage, migrate, collectstatic
from db import getdb, dumpdb, loadrds

env.user = 'ubuntu'
env.chef = '/usr/bin/chef-solo -c solo.rb -j node.json'
env.app_user = 'ccdc'
env.project_dir = '/apps/calaccess/repo/'
env.activate = 'source /apps/calaccess/bin/activate'


@task
def ec2bootstrap():
    """
    Install chef and use it to fully install the application on
    an Amazon EC2 instance.
    """
    # Fire up a new server
    id, host = createserver()

    # Add the new server's host name to the configuration file
    config = yaml.load(open('./config.yml', 'rb'))
    config['host'] = str(host)
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

    print "- Waiting 60 seconds before logging in to configure machine"
    time.sleep(60)

    # Install chef and run it
    installchef()
    cook()

    # Fire up the Django project
    migrate()
    collectstatic()
    restartapache()

    # Done deal
    print(green("Success!"))
    print "Visit the app at %s" % host


@task
def rdsbootstrap():
    """
    Install chef and use it to fully install the database on
    an Amazon RDS instance.
    """
    # Fire up a new server
    host = createrds()

    # Add the new server's host name to the configuration file
    config = yaml.load(open('./config.yml', 'rb'))
    config['host'] = str(host)
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

    # Load the db snapshot
    loadrds()

    print(green("Success!"))


@task(task_class=ConfigTask)
def ssh():
    """
    Log into the EC2 instance using SSH.
    """
    local("ssh %s@%s -i %s" % (env.user, env.hosts[0], env.key_filename[0]))


__all__ = (
    'clonerds',
    'configure',
    'createserver',
    'createrds',
    'dumpdb',
    'getdb',
    'installchef',
    'loadrds',
    'cook',
    'restartapache',
    'rmpyc',
    'pipinstall',
    'manage',
    'migrate',
    'collectstatic',
    'ec2bootstrap',
    'rdsbootstrap',
    'ssh',
)
