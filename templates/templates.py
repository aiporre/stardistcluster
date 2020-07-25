def moab_template(jobName, numberOfNodes, wallTime, memory, email, destination, inputDir, modelName, user, modelDir, outputDir='Null'):
    moab_file_content = "#!/bin/sh\n " \
         "########## Begin MOAB/Slurm header ##########\n" \
         f"#MSUB -N {jobName}\n" \
         "#\n" \
         "# Request number of nodes and CPU cores per node for job\n" \
         f"#MSUB -l nodes={numberOfNodes}:ppn=16:best\n" \
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
         f"python batchstardist.py -d {destination} -i {inputDir} -n {modelDir} -m {modelName} -o {outputDir} > batch_{jobName}.out\n" \
         "exit\n"

    return moab_file_content

def sh_template(user,moab_file):
     sh_file_content = "#!/bin/sh\n" \
                        f"export USER={user} \n" \
                        f"msub $HOME/stardist/{user}/{moab_file}\n"
     return sh_file_content