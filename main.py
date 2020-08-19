from flask import Flask, render_template, session, redirect, url_for, flash,  send_from_directory
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, FloatField
from wtforms.validators import DataRequired, NumberRange, Email
from flask_script import Manager
from utils import get_configuration, save_configuration, create_files, load_files, execute_ssh_command
import time
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
manager = Manager(app)

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('Give a name to a new setup or load your setup', validators=[DataRequired()])
    submit = SubmitField('Create/Load')

class TrainingForm(FlaskForm):
    jobName = StringField('Job Name', validators=[DataRequired()])
    user = StringField('User Name', validators=[DataRequired()])
    numberOfNodes = StringField('Number of Nodes', validators=[DataRequired()])
    wallTime = StringField('Wall time (format HH:MM)', validators=[DataRequired()])
    memory = StringField('Max Memory in mb', validators=[DataRequired()])
    email = StringField('Feedback email', validators=[DataRequired(), Email()])
    inputDir = StringField('Input directory (contains training/validation directories)', validators=[DataRequired()])
    modelDir = StringField('Output directory (model is stored)', validators=[DataRequired()])
    modelName = StringField('Name of the model', validators=[DataRequired()])
    extension = StringField('Extension of the input and target images (e.g. tiff)', validators=[DataRequired()])
    nodeType = StringField('type of node (standard, best, gpu, fat, fat-ivy, best-sky, gpu-sky)', validators=[DataRequired()])
    patchSizeH = IntegerField('Patch Height (px)', validators=[DataRequired()])
    patchSizeW = IntegerField('Patch Width (px)', validators=[DataRequired()])
    patchSizeD = IntegerField('Patch Depth (px)')
    multichannel = BooleanField('2D multichannel image (rgb)')
    saveForFiji = BooleanField('Save model for fiji (only if model is 2D)')
    twoDim = BooleanField('generate a 2D model')
    valFraction = FloatField('Validation fraction', validators=[DataRequired(), NumberRange(min=0.1, max=0.5)])
    submit = SubmitField('Create files')

class PredictionForm(FlaskForm):
    jobName = StringField('Job Name', validators=[DataRequired()])
    user = StringField('User Name', validators=[DataRequired()])
    numberOfNodes = StringField('Number of Nodes', validators=[DataRequired()])
    wallTime = StringField('Wall time (format HH:MM)', validators=[DataRequired()])
    memory = StringField('Max Memory in mb', validators=[DataRequired()])
    memoryUsage = IntegerField('Memory usage %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    email = StringField('Feedback email', validators=[DataRequired(), Email()])
    inputDir = StringField('Input directory (contains tiff images)', validators=[DataRequired()])
    outputDir = StringField('Output directory (predicted labeled images are generated)', validators=[DataRequired()])
    modelDir = StringField('Model directory', validators=[DataRequired()])
    modelName = StringField('Name of the model', validators=[DataRequired()])
    extension = StringField('Extension of the images', validators=[DataRequired()])
    nodeType = StringField('type of node (standard, best, gpu, fat, fat-ivy, best-sky, gpu-sky)',
                           validators=[DataRequired()])
    multichannel = BooleanField('2D multichannel image (rgb)', default=False)
    twoDim = BooleanField('2D image')
    submit = SubmitField('Create files')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html',message=e), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        if session.get('name') is None:
            form.name.data = 'default'
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/training', methods=['GET', 'POST'])
def training():
    form = TrainingForm()
    config = get_configuration(session.get('name'))
    if form.validate_on_submit():
        config['general']['jobName'] = form.jobName.data
        config['general']['user'] = form.user.data
        config['general']['numberOfNodes'] = form.numberOfNodes.data
        config['general']['wallTime'] = form.wallTime.data
        config['general']['memory'] = form.memory.data
        config['general']['email'] = form.email.data
        config['training']['inputDir'] = form.inputDir.data
        config['general']['modelDir'] = form.modelDir.data
        config['training']['modelName'] = form.modelName.data
        config['general']['extension'] = form.extension.data
        config['general']['nodeType'] = form.nodeType.data
        config['training']['patchSizeH'] = str(form.patchSizeH.data)
        config['training']['patchSizeW'] = str(form.patchSizeW.data)
        config['training']['patchSizeD'] = str(form.patchSizeD.data)
        config['2d']['multiChannel'] = str(form.multichannel.data)
        config['2d']['saveForFiji'] = str(form.saveForFiji.data)
        config['2d']['twoDim'] = str(form.twoDim.data)
        config['training']['valFraction'] = str(form.valFraction.data)
        save_configuration(session.get('name'), config)
        create_files(config, destination='training')
        ssh = session.get('ssh') if 'ssh' in session.keys() else None
        load_files(ssh, config, destination='training')
        session['ssh'] = ssh
        return redirect(url_for('training'))
    else:
        form.jobName.default = config['general']['jobName']
        form.user.default = config['general']['user']
        form.numberOfNodes.default = config['general']['numberOfNodes']
        form.wallTime.default = config['general']['wallTime']
        form.memory.default = config['general']['memory']
        form.email.default = config['general']['email']
        form.inputDir.default = config['training']['inputDir']
        form.modelDir.default = config['general']['modelDir']
        form.modelName.default = config['training']['modelName']
        form.extension.default = config['general']['extension']
        form.nodeType.default = config['general']['nodeType']
        form.patchSizeH.default = config['training']['patchSizeH']
        form.patchSizeW.default = config['training']['patchSizeW']
        form.patchSizeD.default = config['training']['patchSizeD']
        form.multichannel.default = config['2d']['multiChannel'] == 'True'
        form.saveForFiji.default = config['2d']['saveForFiji'] == 'True'
        form.twoDim.default = config['2d']['twoDim'] == 'True'
        form.valFraction.default = config['training']['valFraction']
        form.process()
    return render_template('training.html', form=form, name=session.get('name'))

@app.route('/outputs/job/<job>', methods=['GET'])
def job_output(job):
    ssh = session.get('ssh') if 'ssh' in session.keys() else None
    lines = execute_ssh_command(ssh, "cat " + session.get('jobs')[job])
    session['ssh'] = ssh
    return {'job_output_text' : lines.split('\n')}

@app.route('/outputs', methods=['GET'])
def outputs():
    ssh = session.get('ssh') if 'ssh' in session.keys() else None
    lines = execute_ssh_command(ssh, "du -a ./stardist/ | grep .out")
    session['ssh'] = ssh
    def parse_job(line):
        start = line.find('batch_')
        if start<0:
            return '-1'
        start += len('batch_')
        return line[start:-4]
    def parse_path(line):
        start1 = line.find('batch_')
        if start1<0:
            return '-1'
        start2 = line.find('./stardist/')
        return line[start2:]

    current_jobs = [parse_job(line) for line  in lines.split('\n') if not parse_job(line) == '-1']
    current_paths = [parse_path(line) for line in lines.split('\n') if not parse_path(line) == '-1']
    session['jobs'] = {k : v for k, v in zip(current_jobs, current_paths)}
    return render_template('outputs.html', jobs = current_jobs)

@app.route('/jobs', methods=['GET'])
def jobs():
    ssh = session.get('ssh') if 'ssh' in session.keys() else None
    lines = execute_ssh_command(ssh, 'showq')
    session['ssh'] = ssh
    return render_template('jobs.html', lines=lines.split('\n'))

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    form = PredictionForm()
    config = get_configuration(session.get('name'))

    if form.validate_on_submit():
        config['general']['jobName'] = form.jobName.data
        config['general']['user'] = form.user.data
        config['general']['numberOfNodes'] = form.numberOfNodes.data
        config['general']['wallTime'] = form.wallTime.data
        config['general']['memory'] = form.memory.data
        config['prediction']['memoryUsage'] = str(form.memoryUsage.data)
        config['general']['email'] = form.email.data
        config['prediction']['inputDir'] = form.inputDir.data
        config['prediction']['outputDir'] = form.outputDir.data
        config['general']['modelDir'] = form.modelDir.data
        config['prediction']['modelName'] = form.modelName.data
        config['general']['extension'] = str(form.extension.data)
        config['general']['nodeType'] = form.nodeType.data
        config['2d']['multichannel'] = str(form.multichannel.data)
        config['2d']['twoDim'] = str(form.twoDim.data)
        save_configuration(session.get('name'), config)
        create_files(config, destination='prediction')
        ssh = session.get('ssh') if 'ssh' in session.keys() else None
        load_files(ssh, config, destination='prediction')
        session['ssh'] = ssh
        return redirect(url_for('prediction'))
    else:
        form.jobName.default = config['general']['jobName']
        form.user.default = config['general']['user']
        form.numberOfNodes.default = config['general']['numberOfNodes']
        form.wallTime.default = config['general']['wallTime']
        form.memory.default = config['general']['memory']
        form.memoryUsage.default = config['prediction']['memoryUsage']
        form.email.default = config['general']['email']
        form.inputDir.default = config['prediction']['inputDir']
        form.outputDir.default = config['prediction']['outputDir']
        form.modelDir.default = config['general']['modelDir']
        form.modelName.default = config['prediction']['modelName']
        form.extension.default = config['general']['extension']
        form.nodeType.default = config['general']['nodeType']
        form.multichannel.default = config['2d']['multichannel'] == 'True'
        form.twoDim.default = config['2d']['twoDim'] == 'True'
        form.process()
    return render_template('prediction.html', form=form, name=session.get('name'))


# ...
if __name__ == '__main__':
    manager.run()