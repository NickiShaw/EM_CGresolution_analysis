# EM_CGresolution_analysis

A python tool to analyze the resolution of electron microscopy images using the Contrast-to-gradient (CG) method (Ishitani and Sato, 2002).

## Installation

This tool was built to run directly on the command line. There is a conda environment for this tool, if you do not already have conda installed you can do so following [these instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (note: miniconda is sufficient, you do not need to install the whole anaconda package). Then in your terminal install the CG_resolution_env conda environment using:

```
conda env create -f environment.yml

conda activate CG_resolution_env
```

Download the Python folder and note the path, then execute the code by following this format:

```
PATH_TO_CONDA_FOLDER\CG_resolution_env\python.exe PATH_TO_PYTHON_FOLDER_DOWNLOAD/Python/Resolution_v10.py -image PATH_TO_IMAGE\Gold_nanoparticles.jpg -out PATH_TO_OUTPUT_FOLDER  -scale SCALEBAR_VALUE

# e.g. If the scalebar of the image is 50 nm long:
 C:\Users\username\.conda\envs\CG_resolution_env\python.exe C:/Users/username/Desktop/Python/Resolution_v10.py -image C:/Users/username/Desktop/Gold_nanoparticles.jpg -out C:/Users/username/Desktop/output/  -scale 50

```
