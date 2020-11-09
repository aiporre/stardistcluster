## INSTALLATION guide for StarDist Cluster
1. Clone the Github repository

    ```sh
	$ git clone https://github.com/aiporre/stardistcluster
    ```

2. Download anaconda

	https://docs.anaconda.com/anaconda/install/

3. Open the anaconda prompt in Windows or the terminal in Linux

4. Navigate to the installation folder

	`cd path to installation`

5. Run the commands

	[GPU]

	```sh
    $ conda init

	$ conda env create -f environment_gpu.yaml

	$ conda activate stardist-gpu

	$ pip install .
	```

	[CPU]
	```sh
	$ conda init

	$ conda env create -f environment_cpu.yaml

	$ conda activate stardist-cpu

	$ pip install .
	```

6. Install StarDist Cluster on your local machine 

	a. Install Visual Studio if necessary (desktop dev with C++)

	https://visualstudio.microsoft.com/downloads/
	
	b. Remove conda environment, if already created
	```sh
	$ conda remove -n stardist-[cpu or gpu] --all
	```

	c. Install stardist cluster locally
	```sh
	$ pip install csbdeep stardist tensorflow-[cpu or gpu]
	```

7. Run server:
	
    `cd path to installation`

	Copy keys into stardist folder [to access to the BWCLUSTER Heidelberg University] and run the server

    ```sh
    $ pip install flask_bootstrap flask_moment flask_wtf flask_script scp email_validator
	
    $ python main.py runserver
    ```

	Open the server in your favorite browser: http://127.0.0.1:5000/

	To solve the problem with DLL load failed run

    ```sh
    $ conda update --all
    ```

8. Test TF-GPU installation by running:
    ```sh
    $ import tensorflow as tf
    $ print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
	
	$ Num GPUs Available: X
    ```

	Important: if it is not running on GPU do the following
    ```sh
	$ pip uninstall tensorflow
    ```
	or 
    ```sh
	$ pip uninstall tensorflow-gpu
    ```
	or
    ```sh
	$ conda uninstall tensorflow-gpu==1.14
    ```
	and
    ```sh
	$ conda install tensorflow-gpu==1.14
    ```

## RUN StarDist Cluster in the anaconda prompt:

1. Open the conda prompt in Windows or the Linux terminal and type

    ```sh
    $ conda env list
    ```
2. Activate the conda env

    ```sh
    $ conda activate stardist-[cpu or gpu]
    ```
3. Before you run stardist if you get tensorflow GPU out of memory error type

	```sh
	$ export TF_FORCE_GPU_ALLOW_GROWTH=true
	```

OPTION 1

4. Run the server

	```sh
	$ python main.py runserver
	```

	Open the server in your favorite browser: http://127.0.0.1:5000/
	

OPTION 2

5. Navigate to stardist_impl folder and type

	```sh
	$ python train_stardist_3d.py -i "C:\Users\Carlo Beretta\Desktop\test" --image-folder raw --labels-folder label -m modelTest -n "C:\Users\Carlo Beretta\Desktop\test" --patch_size 24 96 96
	```