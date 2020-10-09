def slurm_template(jobName=None,
                  perImage=None,
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
    if destination == "prediction" and perImage:
        second_input = "${2}"
        script_string += f' > ./{user}/batch_{user}_{jobName}_{second_input}.out 2>&1'
    else:
        script_string += f' > ./{user}/batch_{user}_{jobName}.out 2>&1'


    # decide which partition based on the node type
    partition="single"
    if "gpu" in nodeType:
        partition = "gpu-" + partition
    slurm_file_content = "#!/bin/sh\n" \
                        "########## Begin SLURM header ##########\n" \
                        f"#SBATCH --job-name=\"{jobName}\"\n" \
                        "#\n" \
                        "# Request number of nodes and CPU cores per node for job\n" \
                        f"#SBATCH --partition={partition}\n" \
                        f"#SBATCH --nodes=1\n" \
                        f"#SBATCH --ntasks-per-node=16\n" \
                        "# Estimated wallclock time for job\n" \
                        f"#SBATCH --time={wallTime}\n" \
                        "# Memory per processor:\n" \
                        "#\n" \
                        f"#SBATCH --mem={memory}mb\n" \
                        "# Specify a queue class\n" \
                        "# Write standard output and errors in same file\n" \
                        f"#SBATCH -o stardist/{user}/slurm_%j_{user}_{jobName}.log\n" \
                        f"#SBATCH -e stardist/{user}/slurm_%j_{user}_{jobName}.err\n" \
                        "# Send mail when job begins, aborts and ends\n" \
                        "#SBATCH --mail-type=ALL\n" \
                        f"#SBATCH --mail-user={email} \n" \
                        "########### End SLURM header ##########\n" \
                        "#start python script\n" \
                        "cd $HOME/stardist/ \n" \
                        f"export USER={user} \n" \
                        "eval \"$($HOME/miniconda/bin/conda shell.bash hook)\"\n" \
                        "conda activate stardist-gpu \n" \
                        f"{script_string}\n" \
                        "exit\n"

    return slurm_file_content


def sh_template(user, slurm_file, iterImages=None):
    if iterImages is None:
        sh_file_content = "#!/bin/sh\n" \
                          f"export USER={user} \n" \
                          f"sbatch  $HOME/stardist/{user}/{slurm_file}\n" \
                          "echo Done"
    else:
        sh_file_content = "#!/bin/sh\n" \
                          f"FILES={iterImages}/* \n" \
                          f"export USER={user} \n" \
                          "for f in $FILES\n" \
                          "do\n" \
                          "  n=\"$(basename -- $f)\"\n" \
                          "  m=\"$(echo \"$n\" | cut -f 1 -d '.')\"\n" \
                          "  echo \"processing $m file ...\"\n" \
                          f"  sbatch  $HOME/stardist/{user}/{slurm_file} $f $m\n" \
                          "done\n" \
                          "echo Done"
    return sh_file_content

# FILES=/path/to/*
# for f in $FILES
# do
#   echo "Processing $f file..."
#   # take action on each file. $f store current file name
#   cat $f
# done
