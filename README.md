################################################################################################
INSTALLATION gudie for StarDist Cluster

1. Github repository:

	git clone https://github.com/aiporre/stardistcluster

2. Download anaconda:

	https://docs.anaconda.com/anaconda/install/

3. Open anaconda promp

4. Navigate to the installation folder

	F:
	cd <path to installation>

5. Run the commands:

	[gpu]
	conda init
	conda env create -f environment_gpu.yaml
	conda activate stardist-gpu
	pip install .

	[CPU]
	conda init
	conda env create -f environment_cpu.yaml
	conda activate stardist-cpu
	pip install .
	
5.1 Install Visual if necesary (desktop dev with C++)

	https://visualstudio.microsoft.com/downloads/
	(to remove conda environment, if already created)
	conda remove -n stardist-[cpu or gpu] --all

5.2 if you want to run stardist cluster locally install:

	pip install csbdeep stardist tensorflow	

6. run server:

	cd ..
	copy keys into stardistcluster folder
	pip install flask_bootstrap flask_moment flask_wtf flask_script scp email_validator

	python main.py runserver
	open in your favorite browser: http://127.0.0.1:5000/

	This solve the problem with DLL load failed
	conda update --all 

7. Test TF-GPU installation by running:

	import tensorflow as tf
	print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

	Output:

		Num GPUs Available: X

Importatnt: There is a potential bug in the installation of TF-GPU (TD: check conda channel).
If it is not ruinning on GPU do the following:

	pip uninstall tensorflow

or 

	pip uninstall tensorflow-gpu

or

	conda uninstall tensorflow-gpu==1.14

and

	conda install tensorflow-gpu==1.14

################################################################################################
RUN in the anaconda prompt:

1. Open the conda prompt or the linux terminal and type

	conda env list

2. Activate the conda env
	
	conda activate stardist-[cpu or gpu]

3. Only if you run local on Ubuntu OS. Solve tensorflow GPU out of memory error
   TD: Apply the same solution used for the n2v in python. This will solve the problem in Ubuntu and Windows 10

	export TF_FORCE_GPU_ALLOW_GROWTH=true

OPTION 1

	4a. Run the server
	
		python main.py runserver

	5a. Open the server in your favorite browser
	
		open in browser http://127.0.0.1:5000/

OPTION 2

	4b. Navigate to stardistcluster stardist_impl folder 
		
		C:\[PATH_TO_STARDISTCLUSTER]\installation\stardist_impl>


	5b. Adjust the paths and the patch_size and run the python script

		python train_stardist_3d.py -i "C:\Users\Carlo Beretta\Desktop\test" --image-folder raw --labels-folder label -m modelTest -n "C:\Users\Carlo Beretta\Desktop\test" --patch_size 24 96 96
