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

## Features

The following features are command line options that allow manual settings.

# Required:


Term            |  Description
:-------------------------:|:-------------------------:
`-image [PATH]`  | Path to image to be processed
`-out [PATH]`  | Path to desired output folder
`-scale [int]` | Scalebar length (in nm unless otherwise specified)

# Optional:
1.

```
parser.add_argument("-verbose", help="Prints all output messages.", action='store_true')
parser.add_argument("-no_automatic", help="Skips automatic line measurements .", action='store_true')
parser.add_argument("-manual", metavar='M', type=str, nargs='?', help="Takes the path to a spreadsheet of lines and/or ROIs (see wiki for formatting details).")
parser.add_argument("-image", metavar='I', type=str, nargs='?', help="Takes the path to the image to be analysed.")
parser.add_argument("-out", metavar='O', type=str, nargs='?', help="Takes the path to desired output folder.")
parser.add_argument("-show_thresholds", help="Saves light and dark threshold images to help with manual tuning to find scalebar.", action='store_true')

parser.add_argument("-scale", metavar='S', type=int, nargs='?', help="Takes the scalebar length integer.")
parser.add_argument("-scaleunits", metavar='U', type=str, nargs='?', help="Takes the scalebar unit (default = nm).")
parser.add_argument("-max_lines", metavar='N', type=int, nargs='?', help="Takes an integer to set the maximum value of lines taken from the image (default 500).")
parser.add_argument("-line_len", metavar='LL', type=int, nargs='?', help="Takes an integer to set the line length (in pixels), default = 0.03 x the width of the image.")

parser.add_argument("-minimum_contour", metavar='MC', type=int, nargs='?', help="Takes an integer to scale the minimum area of a contour allowed, default = 0.003 * image area.")
parser.add_argument("-manual_scalebar", metavar='MS', type=int, nargs='?', help="Takes an integer as the pixel length of the scalebar (optional, use if scalebar is not automatically located).")
parser.add_argument("-thickness", metavar='T', type=int, nargs='?', help="Takes an integer to set the line thickness, default = 1.")
parser.add_argument("-point_fit_val", metavar='P', type=int, nargs='?', help="Takes an integer to reduce the number of points used to fit the sigmoid, default = 1 (take every point).")
parser.add_argument("-contour_threshold", metavar='C', type=int, nargs='?', help="Takes an integer to set the contour threshold value, default = 140.")
parser.add_argument("-light_threshold", metavar='L', type=int, nargs='?', help="Takes an integer to set the light threshold value for finding the scalebar, default = 50.")
parser.add_argument("-dark_threshold", metavar='D', type=int, nargs='?', help="Takes an integer to set the dark threshold value for finding the scalebar, default = 220.")
```
