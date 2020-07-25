import os, configparser
from shutil import copyfile
from templates.templates import sh_template, moab_template
from paramiko import SSHClient
from cryptography.fernet import Fernet
from scp import SCPClient

def get_configuration(name=None):
    if name is None:
        name = 'default'
    config = configparser.ConfigParser()
    if not os.path.exists('temp/%s.conf' % name):
        copyfile('temp/default.conf', 'temp/%s.conf' % name)
    config.read('temp/%s.conf' % name)
    return config
def save_configuration(name, config):
    if name == 'default' or name is None:
        print('Defaults are not modified')
        pass
    with open('temp/%s.conf' % name, 'w') as configfile:
        config.write(configfile)
def create_files(config, destination='training'):
    moab_file = "config_%s_%s.moab" % (config['general']['jobName'], destination)
    sh_file = 'starjob_%s_%s.sh' % (config['general']['jobName'], destination)

    sh_file_content = sh_template(config['general']['user'], moab_file)
    if destination == 'training':
        moab_file_content = moab_template(config['general']['jobName'],
                                          config['general']['numberOfNodes'],
                                          config['general']['wallTime'],
                                          config['general']['memory'],
                                          config['general']['email'],
                                          destination,
                                          config['training']['inputDir'],
                                          config['training']['modelName'],
                                          config['general']['user'],
                                          config['general']['modelDir'])
    else:
        moab_file_content = moab_template(config['general']['jobName'],
                                          config['general']['numberOfNodes'],
                                          config['general']['wallTime'],
                                          config['general']['memory'],
                                          config['general']['email'],
                                          destination,
                                          config['prediction']['inputDir'],
                                          config['prediction']['modelName'],
                                          config['general']['user'],
                                          config['general']['modelDir'],
                                          outputDir=config['prediction']['outputDir'])

    with open('temp/%s' % moab_file, 'w') as f:
        f.write(moab_file_content)

    with open('temp/%s' % sh_file, 'w') as f:
        f.write(sh_file_content)


def load_files(config, destination='training'):
    key = open("access.key", "rb").read()
    f = Fernet(key)
    with open('user.key', "rb") as file:
        # read all file data
        user_encrypted = file.read()
        user = f.decrypt(user_encrypted)
    with open('password.key', "rb") as file:
        # read all file data
        password_encrypted = file.read()
        password = f.decrypt(password_encrypted)

    # create ssh session in the cluster
    ssh = SSHClient()
    # server = 'bwforcluster.bwservices.uni-heidelberg.de'
    server = '129.206.158.52'
    ssh.load_system_host_keys()
    print('connecting to user', user, 'pwd', password, 'server', server)
    ssh.connect(server, username=user, password=password)
    # create the scp transport client
    scp = SCPClient(ssh.get_transport())

    # create dir USER at fixed directory $HOME/stardist/
    user_dir = '~/stardist/%s' % config['general']['user']
    ssh.exec_command('mkdir -p %s' % user_dir)
    # copy moab generated {jobName}_training.moab to $HOME/stardist/$USER
    moab_file = 'config_%s_%s.moab' % (config['general']['jobName'], destination)
    scp.put('temp/%s' % moab_file, remote_path= user_dir)
    # copy sh generated {jobName}_training.sh to $HOME/stardist/$USER
    sh_file = 'starjob_%s_%s.sh' % (config['general']['jobName'], destination)
    scp.put('temp/%s' % sh_file, remote_path= user_dir)
    # execute job in the cluster i.e submit the jobs
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('bash %s/%s' % (user_dir, sh_file))
    print(ssh_stdout)
    print(ssh_stderr)
