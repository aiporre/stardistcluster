## Installation Guide for Stardist-Cluster

<!--Windows 10 CUDA 10.0-->



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

  

  Open in your favorite browser: http://127.0.0.1:5000/

  

  **Important:** if DLL load fails, update the conda environment

  `$ conda update --all `

  

7. Test TF-GPU installation by running:

  `$ python`

  ```python
import tensorflow as tf
print(">> Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
  ```

  Output:

  ```
  >> Num GPUs Available: X
  ```

  

  **Important:** There is a potential bug in the installation of tensorflow-gpu
  If it is not running on GPU try the following

  `$ pip uninstall tensorflow`

  or 

  `$ pip uninstall tensorflow-gpu`

  or

  `$ conda uninstall tensorflow-gpu==1.14`

  and

  `$ conda install tensorflow-gpu==1.14`



## Run Stardist-Cluster in the Anaconda Prompt

1. Open the conda prompt or the linux terminal and type

  `$ conda env list`

  

2. Activate the conda env

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

```
$ python train_stardist_3d.py -i "[PATH_TO_IMAGE_FOLDER]" --image "[RAW_IMAGE_SUBFOLDER_NAME]" --labels "[LABEL_IMAGE_SUBFOLDER_NAME]" -n "[MODEL_PATH]" -m "[MODEL_NAME]" --patch_size 24 96 96
```



#### **<u>Prediction</u>**

Adjust the path and run the python script `predict_stardist_3d.py`

```
$ predict_stardist_3d -i "[PATH_TO_THE_IMAGES]" -o "[PATH_TO_THE_OUTPUT]" -n "[MODEL_PATH]" -m "[MODEL_NAME]" -r 50
```

**NB:** `--r` is the number of blocks [100 = No blocks]

**Tip:** Increase the number of blocks by reducing `--r` to process large data. However, increasing the number of blocks increase the computational time