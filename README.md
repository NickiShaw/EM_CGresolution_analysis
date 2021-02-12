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

### Required:

Term            |  Description
:-------------------------:|:-------------------------:
`-image [PATH]`  | Path to image to be processed
`-out [PATH]`  | Path to desired output folder
`-scale [int]` | Scalebar length (in nm unless otherwise specified)

### Optional:

Term            |  Description
:-------------------------:|:-------------------------:
`-verbose`  | Prints all output messages
`-no_automatic`  | Skips any automatic line profile processing (note, set `-manual` to use manual search, otherwise no line profiles will be found)
`-manual [PATH]` | Takes the path to a spreadsheet of lines and/or ROIs (see [wiki](https://github.com/NickiShaw/EM_CGresolution_analysis/wiki/Manual-Options) for formatting details)
`-thickness [int]` | Takes an integer to set the line thickness used for averaging pixel intensities, default = 1.
`-show_thresholds` | Saves light and dark threshold images to help with manual tuning to find scalebar
`-contour_threshold [int]` | Takes an integer to set the contour threshold value, default = 140
`-light_threshold [int]` | Takes an integer to set the light threshold value for finding the scalebar, default = 50
`-dark_threshold [int]` | Takes an integer to set the dark threshold value for finding the scalebar, default = 220
`-scaleunits [str]` | Takes alternative scalebar units (e.g. mm, the default is nm)
`-max_lines [int]` | Takes an integer to set the maximum value of lines taken from the image (default 500)
`line_len [int]` | Takes an integer to set the line length (in pixels), default = 0.03 x the width of the image
`-minimum_contour [int]` | Takes an integer to scale the minimum area of a contour allowed, default = 0.003 * image
`-manual_scalebar [int]` | Takes an integer as the pixel length of the scalebar (optional, use if scalebar is not automatically located)
`-point_fit_val [int]` | Takes an integer to reduce the number of points used to fit the sigmoid, default = 1 (take every point), *note this should be set to 5 to reduce the runtime for approximate results*

## Outputs

All the output is stored in a single folder named with the date and time for the run. This is to avoid accidentally overwriting the content of a previous run.

A standard run outputs the following:
1. The image with the scalebar highlighted in red.
2. Images with the line profile location indicated in red, with the line number indicated in the filename.
3. Graphs showing the intensities across line profile fitted to a sigmoid curve, the line numbers are  also indicated in the filenames for easy searching.
4. The same images as in 3., but including the 'bounding lines' used to calculate the 25% and 75% boundaries and resolution.
5. The contour thresholded image and another image with all the contours outlined in red.
6. run_info.txt which stores all the options used in the run which are useful to record for future reference and to ensure runs can be replicated on later images.
7. output.csv with the following information:

Line_Number | R_squared_value | Resolution (units) |	X1 | Y1 |	X2 | Y2
-|-|-|-|-|-|-|
Automatic line #/ Manual line #/ Automatic line # in ROI # | r^2 | resolution |	X1 | Y1 |	X2 | Y2

![sample_output_image](https://github.com/NickiShaw/EM_CGresolution_analysis/blob/main/Wiki_Pictures/sample_outputs.jpg?raw=true)

Where X1, Y1, X2, Y2 are the two points that make up the line for that line profile.
