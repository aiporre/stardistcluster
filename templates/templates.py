def moab_template(jobName=None,
                  numberOfNodes=None,
                  wallTime=None,
                  memory=None,
                  email=None,
                  destination=None,
                  inputDir=None,
                  modelName=None,
                  user=None,
                  modelDir=None,
                  twoDim=None,
                  patchSizeH=None,
                  patchSizeW=None,
                  patchSizeD=None,
                  valFraction=None,
                  extension=None,
                  nodeType=None,
                  saveForFiji=None,
                  multichannel=None,
                  outputDir=None,
                  memory_usage=None):
    twoDim = twoDim == 'True'
    multichannel = multichannel == 'True'
    saveForFiji = saveForFiji == 'True'
    print('twoDim', twoDim)
    print('multichannel', multichannel)
    print('saveForFiji', saveForFiji)
    if destination == 'training' and twoDim:
        script_string = f'train_stardist_2d -i {inputDir} -n {modelDir} -m {modelName}'
    elif destination == 'prediction' and twoDim:
        script_string = f'predict_stardist_2d -i {inputDir} -n {modelDir} -m {modelName} -o {outputDir}'
    elif destination == 'training' and not twoDim:
        script_string = f'train_stardist_3d -i {inputDir} -n {modelDir} -m {modelName}'
    else:
        script_string = f'predict_stardist_3d -i {inputDir} -n {modelDir} -m {modelName} -o {outputDir}'
    if multichannel and twoDim:
        script_string += ' --multichannel'
    if twoDim and destination == 'training':
        script_string += ' '.join([' -p', patchSizeH, patchSizeW])
    elif not twoDim and destination == 'training':
        script_string += ' '.join([' -p', patchSizeH, patchSizeW, patchSizeD])

    if destination == 'training':
        script_string += f' -s {valFraction}'

    script_string += f' --ext {extension}'
    if twoDim and saveForFiji:
        script_string += ' --save-for-fiji'
    if destination == "prediction" and memory_usage is not None and not memory_usage == "100":
        script_string += f' -r {memory_usage}'

    script_string += f' > ./{user}/batch_{jobName}.out 2>&1'

    moab_file_content = "#!/bin/sh\n" \
                        "########## Begin MOAB/Slurm header ##########\n" \
                        f"#MSUB -N {jobName}\n" \
                        "#\n" \
                        "# Request number of nodes and CPU cores per node for job\n" \
                        f"#MSUB -l nodes={numberOfNodes}:ppn=16:{nodeType}\n" \
                        "# Estimated wallclock time for job\n" \
                        f"#MSUB -l walltime={wallTime}\n" \
                        "# Memory per processor:\n" \
                        "#\n" \
                        f"#MSUB -l mem={memory}mb\n" \
                        "# Specify a queue class\n" \
                        "# Write standard output and errors in same file\n" \
                        "#MSUB -j oe\n" \
                        "# Send mail when job begins, aborts and ends\n" \
                        "#MSUB -m bae\n" \
                        f"#MSUB -M {email} \n" \
                        "########### End MOAB header ##########\n" \
                        "echo 'Submit Directory:                     $MOAB_SUBMITDIR' \n" \
                        "echo 'Working Directory:                    $PWD'\n" \
                        "echo 'Running on host                       $HOSTNAME'\n" \
                        "echo 'Job id:                               $MOAB_JOBID'\n" \
                        "echo 'Job name:                             $MOAB_JOBNAME'\n" \
                        "echo 'Number of nodes allocated to job:     $MOAB_NODECOUNT'\n" \
                        "echo 'Number of cores allocated to job:     $MOAB_PROCCOUNT'\n" \
                        "#start python script\n" \
                        "cd $HOME/stardist/ \n" \
                        f"export USER={user} \n" \
                        "eval \"$($HOME/miniconda/bin/conda shell.bash hook)\"\n" \
                        "conda activate stardist-gpu \n" \
                        f"{script_string}\n" \
                        "exit\n"

    return moab_file_content


def sh_template(user, moab_file):
    sh_file_content = "#!/bin/sh\n" \
                      f"export USER={user} \n" \
                      f"msub $HOME/stardist/{user}/{moab_file}\n" \
                      "echo Done"
    return sh_file_content
