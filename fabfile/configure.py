import os
import yaml
from fabric.tasks import Task
from os.path import expanduser
from fabric.colors import green
from fabric.api import task, env


def require_input(prompt):
    """
    Demand input from the user.
    """
    i = None
    while not i:
        i = raw_input(prompt.strip()+' ')
        if not i:
            print '  I need this, please.'
    return i


@task
def configure():
    """
    Create a configuration file that stores your credentials to a secret file.
    """
    config = {}

    print('')
    print('AWS configuration')
    print('=================')
    print('')

    # Request data from the user
    config['AWS_ACCESS_KEY_ID'] = require_input('Your AWS access key [Required]:')
    config['AWS_SECRET_ACCESS_KEY'] = require_input('Your AWS secret key [Required]:')
    config['key_name'] = require_input('Your AWS key name [Required]:')
    config['AWS_REGION'] = raw_input("Target AWS region [Default: us-west-2]:") or 'us-west-2'
    config['EC2_INSTANCE_TYPE'] = raw_input("Target EC2 instance size [Default: m3.medium]:") or 'm3.medium'
    config['AWS_SECURITY_GROUP'] = raw_input("Target security group [Default: default]:") or 'default'

    # Write it to a YAML file
    config_file = open('./config.yml', 'w')
    config_file.write(yaml.dump(config, default_flow_style=False))
    config_file.close()

    print('')
    print(green('That\'s it. All set up!'))
    print('Configuration saved in config.yml')
    print('')


def loadconfig():
    """
    Load secret credentials from the YAML configuration file
    """
    if not os.path.exists('./config.yml'):
        configure()
    config = yaml.load(open('./config.yml', 'rb'))
    try:
        env.AWS_ACCESS_KEY_ID = config['AWS_ACCESS_KEY_ID']
        env.AWS_SECRET_ACCESS_KEY = config['AWS_SECRET_ACCESS_KEY']
        env.key_name = config['key_name']
        env.key_filename = (expanduser("~/.ec2/%s.pem" % env.key_name),)
        env.AWS_REGION = config['AWS_REGION']
        env.EC2_INSTANCE_TYPE = config['EC2_INSTANCE_TYPE']
        env.AWS_SECURITY_GROUP = config['AWS_SECURITY_GROUP']
    except (KeyError, TypeError):
        pass
    try:
        env.hosts = [config['host'],]
        env.host = config['host']
        env.host_string = config['host']
    except (KeyError, TypeError):
        pass


class ConfigTask(Task):
    def __init__(self, func, *args, **kwargs):
        super(ConfigTask, self).__init__(*args, **kwargs)
        self.func = func

    def __call__(self):
        self.run()

    def run(self, *args, **kwargs):
        loadconfig()
        return self.func(*args, **kwargs)
