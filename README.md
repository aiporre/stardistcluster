<<<<<<< HEAD
## Installation Guide for Stardist-Cluster
=======
## INSTALLATION guide for StarDist Cluster
1. Clone the Github repository
>>>>>>> master

<!--Windows 10 CUDA 10.0-->

<<<<<<< HEAD
=======
2. Download anaconda
>>>>>>> master


1. Clone the *GitHub* repository

  `$ git clone https://github.com/aiporre/stardistcluster`

  

2. Download *anaconda* if not yet installed and follow the installation instructions

  https://docs.anaconda.com/anaconda/install/

  

3. Open the anaconda prompt

   

4. Navigate to the installation folder

  ```
  $ F:
  $ cd <path to installation>
  ```

  

5. Run the command:

  ```
  [gpu]
  $ conda init
  $ conda env create -f environment_gpu.yaml
  $ conda activate stardist-gpu
  $ pip install .
  ```

  ```
  [CPU]
  $ conda init
  $ conda env create -f environment_cpu.yaml
  $ conda activate stardist-cpu
  $ pip install .
  ```

  

  Install *Visual Studio* if not installed (desktop dev with C++)

  https://visualstudio.microsoft.com/downloads/

  

  **Important:** remove the conda environment, if already created
  `$ conda remove -n stardist-[cpu or gpu] --all`

  

  If you want to run stardist-cluster locally install

  `$ pip install csbdeep stardist tensorflow`

  

6. Run the server:

  Copy keys into stardist-cluster folder and run the following commands

  ```
  $ pip install flask_bootstrap flask_moment flask_wtf flask_script scp email_validator
  
  $ python main.py runserver
  ```

  

<<<<<<< HEAD
  Open in your favorite browser: http://127.0.0.1:5000/

  
=======
5. Run the commands

	[GPU]
>>>>>>> master

  **Important:** if DLL load fails, update the conda environment

  `$ conda update --all `

  

7. Test TF-GPU installation by running:

<<<<<<< HEAD
  `$ python`
=======
	[CPU]
	```sh
	$ conda init
>>>>>>> master

  ```python
import tensorflow as tf
print(">> Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
  ```

  Output:

  ```
  >> Num GPUs Available: X
  ```

<<<<<<< HEAD
  

  **Important:** There is a potential bug in the installation of tensorflow-gpu
  If it is not running on GPU try the following

  `$ pip uninstall tensorflow`
=======
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
>>>>>>> master

  or 

<<<<<<< HEAD
  `$ pip uninstall tensorflow-gpu`

  or

  `$ conda uninstall tensorflow-gpu==1.14`

  and
=======
	Copy keys into stardist folder [to access to the BWCLUSTER Heidelberg University] and run the server

    ```sh
    $ pip install flask_bootstrap flask_moment flask_wtf flask_script scp email_validator
	
    $ python main.py runserver
    ```

	Open the server in your favorite browser: http://127.0.0.1:5000/

	To solve the problem with DLL load failed run
>>>>>>> master

  `$ conda install tensorflow-gpu==1.14`

<<<<<<< HEAD


## Run Stardist-Cluster in the Anaconda Prompt
=======
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
>>>>>>> master

1. Open the conda prompt or the linux terminal and type

  `$ conda env list`

  

2. Activate the conda env

<<<<<<< HEAD
   `$ conda activate stardist-[cpu or gpu]`

   

3. Only if you run local on Ubuntu OS. Solve tensorflow GPU out of memory error
   TD: Apply the same solution used for the n2v in python. This will solve the problem in Ubuntu and Windows 10

   ` $ export TF_FORCE_GPU_ALLOW_GROWTH=true`

   

#### **<u>Training</u>**

*<u>OPTION 1</u>*

Run the server

`$ python main.py runserver`



Open the link in your favorite browser 

http://127.0.0.1:5000/



*<u>OPTION 2</u>*

Navigate to stardist-cluster <<stardist_impl>> folder 

`$ C:\[PATH_TO_STARDISTCLUSTER]\installation\stardist_impl`



Adjust the path, the patch_size and run the python script `train_stardist_3d.py`

**NB:** The input path to the images has to contain 2 subfolders, one with the raw images and the other one with the label images
=======
    ```sh
    $ conda activate stardist-[cpu or gpu]
    ```
3. Before you run stardist if you get tensorflow GPU out of memory error type
>>>>>>> master

```
$ python train_stardist_3d.py -i "[PATH_TO_IMAGE_FOLDER]" --image "[RAW_IMAGE_SUBFOLDER_NAME]" --labels "[LABEL_IMAGE_SUBFOLDER_NAME]" -n "[MODEL_PATH]" -m "[MODEL_NAME]" --patch_size 24 96 96
```



#### **<u>Prediction</u>**

<<<<<<< HEAD
Adjust the path and run the python script `predict_stardist_3d.py`
=======
	Open the server in your favorite browser: http://127.0.0.1:5000/
	
>>>>>>> master

```
$ predict_stardist_3d -i "[PATH_TO_THE_IMAGES]" -o "[PATH_TO_THE_OUTPUT]" -n "[MODEL_PATH]" -m "[MODEL_NAME]" -r 50
```

<<<<<<< HEAD
**NB:** `--r` is the number of blocks [100 = No blocks]
=======
5. Navigate to stardist_impl folder and type
>>>>>>> master

**Tip:** Increase the number of blocks by reducing `--r` to process large data. However, increasing the number of blocks increase the computational time