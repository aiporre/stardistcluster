import json
import os, configparser
from shutil import copyfile
from templates.templates import sh_template, slurm_template
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

def run_local(config, destination='training'):
    from stardist_impl import train2d, train3d, predict2d, predict3d
    if destination == 'training':
        inputDir = config['training']['inputDir']
        modelDir = config['general']['modelDir']
        modelName = config['training']['modelName']
        twoDim = config['2d']['twoDim']
        patchSizeH = int(config['training']['patchSizeH'])
        patchSizeW = int(config['training']['patchSizeW'])
        patchSizeD = int(config['training']['patchSizeD'])
        valFraction = config['training']['valFraction']
        extension = config['general']['extension']
        saveForFiji = config['2d']['saveForFiji']
        multichannel = config['2d']['multichannel']

        twoDim = twoDim == 'True'
        multichannel = multichannel == 'True'
        saveForFiji = saveForFiji == 'True'
        model_path = os.path.join(modelDir, modelName)

        if twoDim:
            train2d(inputDir,
                     model_path,
                     "images",
                     "labels",
                     extension,
                     valFraction,
                     tuple([int(patchSizeW), int(patchSizeH)]),
                     multichannel,
                     saveForFiji)
        else:
            train3d(inputDir,
                     model_path,
                     "images",
                     "labels",
                     extension,
                     valFraction,
                     tuple([int(patchSizeD), int(patchSizeW), int(patchSizeH)]),
                     anisotropy=None)
    else:
        inputDir = config['prediction']['inputDir']
        modelDir = config['general']['modelDir']
        modelName = config['training']['modelName']
        twoDim = config['2d']['twoDim']
        extension = config['general']['extension']
        multichannel = config['2d']['multichannel']
        outputDir = config['prediction']['outputDir']
        memory_usage = int(config['prediction']['memoryUsage'])

        twoDim = twoDim == 'True'
        multichannel = multichannel == 'True'
        model_path = os.path.join(modelDir, modelName)
        if twoDim == 'True':
            predict2d(model_path, inputDir, outputDir, extension, multichannel, memory_usage)
        else:
            predict3d(model_path, inputDir, outputDir, extension, memory_usage)

def create_files(config, destination='training'):
    slurm_file = "config_%s_%s.slurm" % (config['general']['jobName'], destination)
    sh_file = 'starjob_%s_%s.sh' % (config['general']['jobName'], destination)
    if destination == 'prediction' and config['general']['manyImgPerNode'] == 'False':
        # ssh content create one image per node, therefore iterate over the images in input dir
        sh_file_content = sh_template(config['general']['user'], slurm_file, iterImages=config['prediction']['inputDir'])
    else:
        sh_file_content = sh_template(config['general']['user'], slurm_file)
    if destination == 'training':
        slurm_file_content = slurm_template(jobName=config['general']['jobName'],
                                          wallTime=config['general']['wallTime'],
                                          memory=config['general']['memory'],
                                          email=config['general']['email'],
                                          destination=destination,
                                          inputDir=config['training']['inputDir'],
                                          modelName=config['training']['modelName'],
                                          user=config['general']['user'],
                                          modelDir=config['general']['modelDir'],
                                          twoDim = config['2d']['twoDim'],
                                          patchSizeH = config['training']['patchSizeH'],
                                          patchSizeW = config['training']['patchSizeW'],
                                          patchSizeD = config['training']['patchSizeD'],
                                          valFraction = config['training']['valFraction'],
                                          extension = config['general']['extension'],
                                          nodeType=config['general']['nodeType'],
                                          saveForFiji = config['2d']['saveForFiji'],
                                          multichannel = config['2d']['multichannel'])

    else:
        if config['general']['manyImgPerNode'] == 'True':
            inputDir = config['prediction']['inputDir']
            perImage = False
        else:
            inputDir = "${1}"
            perImage = True

        slurm_file_content = slurm_template(jobName=config['general']['jobName'],
                                          perImage= perImage,
                                          wallTime=config['general']['wallTime'],
                                          memory=config['general']['memory'],
                                          email=config['general']['email'],
                                          destination=destination,
                                          inputDir=inputDir,
                                          modelName=config['prediction']['modelName'],
                                          user=config['general']['user'],
                                          modelDir=config['general']['modelDir'],
                                          twoDim=config['2d']['twoDim'],
                                          extension=config['general']['extension'],
                                          nodeType=config['general']['nodeType'],
                                          multichannel=config['2d']['multichannel'],
                                          outputDir=config['prediction']['outputDir'],
                                          memory_usage=config['prediction']['memoryUsage'])

    with open('temp/%s' % slurm_file, 'w') as f:
        f.write(slurm_file_content)

    with open('temp/%s' % sh_file, 'w') as f:
        f.write(sh_file_content)
def get_ssh_client():
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
    server = 'bwforcluster.bwservices.uni-heidelberg.de'
    ssh.load_system_host_keys()
    ssh.connect(server, username=user, password=password)
    return ssh

def _execute_command(ssh, command):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    print('execute command :', command)
    out = ssh_stdout.read().decode().strip()
    error = ssh_stdout.read().decode().strip()
    print('OUT:', out)
    if len(error)>0:
        print('ERROR:', error)
    return out + '\n' + error

def execute_ssh_command(ssh, command):
    if ssh is None or ssh.get_transport() is None or not ssh.get_transport().is_active():
        ssh = get_ssh_client()
    return _execute_command(ssh, command)


def load_files(ssh, config, destination='training'):

    if ssh is None or ssh.get_transport() is None or not ssh.get_transport().is_active():
        ssh = get_ssh_client()
    # create the scp transport client
    scp = SCPClient(ssh.get_transport())

    # create dir USER at fixed directory $HOME/stardist/
    user_dir = '~/stardist/%s' % config['general']['user']
    ssh.exec_command('mkdir %s' % user_dir)
    print('Creating directory ', user_dir)
    # copy slurm generated {jobName}_training.slurm to $HOME/stardist/$USER
    slurm_file = 'config_%s_%s.slurm' % (config['general']['jobName'], destination)
    scp.put('temp/%s' % slurm_file, remote_path= user_dir)
    print('moving slurm_file', slurm_file, 'to ', user_dir)
    # copy sh generated {jobName}_training.sh to $HOME/stardist/$USER
    sh_file = 'starjob_%s_%s.sh' % (config['general']['jobName'], destination)
    scp.put('temp/%s' % sh_file, remote_path= user_dir )
    print('moving sh file', sh_file, 'to ', user_dir)
    scp.close()
    # execute job in the cluster i.e submit the jobs
    _execute_command(ssh, 'vi %s/%s -c \'set ff=unix\' -c \'x\'' % (user_dir, sh_file))
    _execute_command(ssh, 'vi %s/%s -c \'set ff=unix\' -c \'x\'' % (user_dir, slurm_file))
    _execute_command(ssh, 'bash %s/%s' % (user_dir, sh_file))
    return ssh