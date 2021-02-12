
import cv2
from matplotlib import pyplot as plt
from PIL import Image
import math as m
import numpy as np
import sys
import pandas as pd
from Image_features_v2 import *
import datetime
import csv
import os
import argparse

parser = argparse.ArgumentParser()
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


args = parser.parse_args()

# "-image" takes the path to the image to be analysed.
if args.image != None:
    image_path = args.image
else:
    sys.exit("An image is required, flag '-image [I]'.")
    # image_path = "C:\\Users\\shawn\\Desktop\\W2021_coop\\resolution\\Gold_nanoparticles.jpg"

# "-out" takes the path to the output folder.
if args.out != None:
    output_dir = args.out + "\\"
else:
    sys.exit("An image is required, flag '-image [I]'.")
    # output_dir = "C:\\Users\\shawn\\Desktop\\W2021_coop\\resolution\\output\\"

# "-verbose" prints all outputs.
if args.show_thresholds:
    show_thresholds = True
else:
    show_thresholds = False


# "-verbose" prints all outputs.
if args.verbose:
    print_info = True
else:
    print_info = False

# "-no_automatic" removes automatic run.
if args.no_automatic:
    no_automatic = True
else:
    no_automatic = False

# "-thickness" with int sets alternative thickness (default 1).
if args.manual_scalebar != None:
    manual_scalebar = args.manual_scalebar
    find_scalebar = False
else:
    find_scalebar = True

# "-thickness" with int sets alternative thickness (default 1).
if args.thickness != None:
    thickness = args.thickness
else:
    thickness = 1

# "-thickness" with int sets alternative thickness (default 1).
if args.minimum_contour != None:
    minimum_contour = args.minimum_contour
else:
    minimum_contour = 0.005

# "-point_fit_val" with int reduces the number of points used to fit the sigmoid (default 1).
if args.point_fit_val != None:
    point_scale_fit = args.point_fit_val
else:
    point_scale_fit = 1

# "-contour_threshold" with int sets alternative contour threshold value (default 140).
if args.contour_threshold != None:
    contour_threshold_setting = args.contour_threshold
else:
    contour_threshold_setting = 140

# "-contour_threshold" with int sets alternative contour threshold value (default 140).
if args.light_threshold != None:
    light_threshold_setting = args.light_threshold
else:
    light_threshold_setting = 50

# "-contour_threshold" with int sets alternative contour threshold value (default 140).
if args.dark_threshold != None:
    dark_threshold_setting = args.dark_threshold
else:
    dark_threshold_setting = 220

# "-scale" with int sets the scalebar length value (required).
if args.scale != None:
    sclbr_realsize_num = args.scale
else:
    sys.exit("A scalebar length value is required, flag '-scale [S]'.")
    # sclbr_realsize_num = 50

# "-scaleunits" with int sets scalebar units (default nm).
if args.scaleunits != None:
    sclbr_realsize_index = args.scaleunits
else:
    sclbr_realsize_index = 'nm'

# "-max_lines" with int sets the maximum value of lines taken from the image (default 500).
if args.scaleunits != None:
    max_lines = args.max_lines
else:
    max_lines = 500

# "-manual" with int sets the maximum value of lines taken from the image (default 500).
if args.manual != None:
    manual_path = args.manual
    # manual_path = "C:\\Users\\shawn\\Desktop\\W2021_coop\\resolution\\Point coordinates of Gold Nanoparticles.csv" # for testing.
    manual_option = True
else:
    manual_option = False

# Save the arguments in the run txt file for repetition.
all_arguments = str(args)


# Make folder for each individual run to avoid overwriting previous output.
time = str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")
output_dir = output_dir + "\\" + time + "\\"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Read in image.
img = cv2.imread(image_path)

# Get dimensions of image.
img_height, img_width, _ = img.shape
img_area = img_height * img_width

# Set line widths for profile.
# "-line_len" with int sets alternative thickness (default 1).
if args.line_len != None:
    line_length = args.line_len
else:
    line_length = img_width * 0.03

# Testing variables set to False.
show_scalebar = False
show_contour_threshold = False
show_contours = False
show_tangentsandnormals = False
debug = False

#############################################################
# Get scalebar
#############################################################
if find_scalebar:
    scbr_img = img.copy()

    # Get contours for light and dark thresholds.
    lightcontour, a = getContours(scbr_img, light_threshold_setting, 255)
    darkcontour, b = getContours(scbr_img, dark_threshold_setting, 255)

    if show_thresholds:
        cv2.imwrite(str(output_dir) + "light_threshold.jpg", a)
        cv2.imwrite(str(output_dir) + "dark_threshold.jpg", b)

    # Make as ContourSet objects.
    light_contour = ContourSet(lightcontour, img_width, img_height)
    dark_contour = ContourSet(lightcontour, img_width, img_height)

    # Get widths of the scalebars found for each threshold
    index_light, width_light = light_contour.getScalebar()
    index_dark, width_dark = dark_contour.getScalebar()

    # Choose the longest contour from the two thresholds.
    if width_light >= width_dark:
        sclbr_width = width_light
        cnts = lightcontour
        ix = index_light
    else:
        sclbr_width = width_dark
        cnts = darkcontour
        ix = index_dark

    # Draw contours to show scalebar was located, outputs image for every run.
    cv2.drawContours(scbr_img, cnts, ix, (255, 0, 0), 3)
    plt.imshow(scbr_img, cmap='gray')
    cv2.imwrite(str(output_dir) + "scalebar.jpg", cv2.cvtColor(scbr_img, cv2.COLOR_BGR2RGB))
    if show_scalebar:
        print("The scalebar is " + str(sclbr_width) + " px long.")
        plt.show()
else:
    sclbr_width = manual_scalebar

pixel_over_realsize = sclbr_realsize_num / sclbr_width

#############################################################
# Get resolution using CG method
#############################################################
prtcle_img = img.copy()

# Apply threshold for finding all particle contours.
prtcle_contours, threshold_img = getContours(prtcle_img, contour_threshold_setting, 255)

# Output thresholded image.
cv2.imwrite(str(output_dir) + "contour_threshold.jpg", threshold_img)

if show_contour_threshold:
    plt.imshow(threshold_img, cmap='gray')
    plt.show()

# Filter out small contours (noise) and parts touching the edges of the image.
particle_contours = ContourSet(prtcle_contours, img_width, img_height)
filtered_contours, contour_points = particle_contours.filterSmallContours(minimum_contour)

# Output contours image.
cv2.drawContours(prtcle_img, filtered_contours, -1, (255, 0, 0), 2)
cv2.imwrite(str(output_dir) + "contours.jpg", cv2.cvtColor(prtcle_img, cv2.COLOR_BGR2RGB))

# Draw particle contours.
if show_contours:
    plt.imshow(prtcle_img, cmap='gray')
    plt.show()

# Half the number of points until there are less than 1000
while (len(contour_points) > max_lines):
    contour_points = contour_points[1::2]

# Round the length of the contour list down to an even number (so each point makes a pair for line drawing).
even_number = m.floor(len(contour_points) / 2) * 2

# Make copy of image for showing tangent and normal lines.
line_img = img.copy()

# Get tangent lines and show on image in red and green lines.
tangent_points = []
normal_points = []
for i in range(0, even_number, 2):
    two_points = PointPair(contour_points[i], contour_points[i + 1], line_length)
    tangent_line = two_points.getscaledTangent()
    normal_line = two_points.getnewNormal()
    tangent_points.append(tangent_line)
    normal_points.append(normal_line)
    cv2.line(line_img, tangent_line[0], tangent_line[1], (0, 255, 0), 2)
    cv2.line(line_img, normal_line[0], normal_line[1], (255, 0, 0), 2)

if show_tangentsandnormals:
    plt.imshow(line_img, cmap='gray')
    plt.show()

res_list = []
r2_list = []
name = []
x1_output = []
y1_output = []
x2_output = []
y2_output = []

# Automatically found lines.
if not no_automatic:
    for t in range(len(normal_points)):
        automatic_prefix = "Automatic line " + str(t)
        automatic_resolution = Resolution(normal_points[t], thickness, img, point_scale_fit, line_length,
                                          pixel_over_realsize, sclbr_realsize_index, debug, print_info, output_dir)
        res_a = automatic_resolution.getResolution(automatic_prefix)
        if res_a != None:
            res_list.append(res_a[0])
            r2_list.append(res_a[1])
            name.append(automatic_prefix)
            x1_output.append(normal_points[t][0][0])
            y1_output.append(normal_points[t][0][1])
            x2_output.append(normal_points[t][1][0])
            y2_output.append(normal_points[t][1][1])


if manual_option:
    manual_df = Spreadsheet(pd.read_csv(manual_path, dtype=str))
    manual_points = manual_df.import_all_manual_data()[0]
    manual_ROIs = manual_df.import_all_manual_data()[1]


# Manually set lines
if manual_option and manual_points != []:
    manu_res = []
    manu_r2 = []
    manu_i = []
    # Run resolution function.
    for t in range(len(manual_points)):
        manual_prefix = "Manual line " + str(t)
        manual_resolution = Resolution(manual_points[t], thickness, img, point_scale_fit, line_length,
                                      pixel_over_realsize, sclbr_realsize_index, debug, print_info, output_dir)
        res_m = manual_resolution.getResolution(manual_prefix)
        if res_m != None:
            res_list.append(res_m[0])
            r2_list.append(res_m[1])
            name.append(manual_prefix)
            x1_output.append(manual_points[t][0][0])
            y1_output.append(manual_points[t][0][1])
            x2_output.append(manual_points[t][1][0])
            y2_output.append(manual_points[t][1][1])
        # For manually set lines show if the selection failed.
        else:
            res_list.append("failed")
            r2_list.append("failed")
            name.append(manual_prefix)
            x1_output.append(manual_points[t][0][0])
            y1_output.append(manual_points[t][0][1])
            x2_output.append(manual_points[t][1][0])
            y2_output.append(manual_points[t][1][1])


# Automatic lines from ROI.
if manual_option and manual_ROIs != []:
    manual_ROIs = manual_df.import_all_manual_data()[1]
    for box in manual_ROIs:
        x, y, w, h = box
        # Crop the image to the ROI.
        ROI = img[y:y+h, x:x+w]

        # Apply threshold for finding all particle contours.
        ROI_prtcle_contours, ROI_threshold_img = getContours(ROI, contour_threshold_setting, 255)

        if show_contour_threshold:
            plt.imshow(ROI_threshold_img, cmap='gray')
            plt.show()

        # Filter out small contours (noise) and parts touching the edges of the image.
        ROI_particle_contours = ContourSet(ROI_prtcle_contours, w, h)
        ROI_filtered_contours, ROI_contour_points = ROI_particle_contours.filterSmallContours()

        # Draw particle contours.
        if show_contours:
            cv2.drawContours(ROI, ROI_filtered_contours, -1, (255, 0, 0), 2)
            plt.imshow(ROI, cmap='gray')
            plt.show()

        # Half the number of points until there are less than 1000
        while (len(ROI_contour_points) > max_lines):
            ROI_contour_points = ROI_contour_points[1::2]

        # Round the length of the contour list down to an even number (so each point makes a pair for line drawing).
        even_number = m.floor(len(ROI_contour_points) / 2) * 2

        # Make copy of image for showing tangent and normal lines.
        ROI_line_img = img.copy()

        # Get tangent lines and show on image in red and green lines.
        ROI_tangent_points = []
        ROI_normal_points = []
        for v in range(0, even_number, 2):
            ROI_two_points = PointPair(ROI_contour_points[v], ROI_contour_points[v + 1], line_length)
            ROI_tangent_line = ROI_two_points.getscaledTangent()
            ROI_normal_line = ROI_two_points.getnewNormal()
            # Transform tangent and normal lines into the ROI space of the original image.
            ROI_tangent_line = [(ROI_tangent_line[0][0] + x, ROI_tangent_line[0][1] + y), (ROI_tangent_line[1][0] + x, ROI_tangent_line[1][1] + y)]
            ROI_normal_line = [(ROI_normal_line[0][0] + x, ROI_normal_line[0][1] + y), (ROI_normal_line[1][0] + x, ROI_normal_line[1][1] + y)]
            ROI_tangent_points.append(ROI_tangent_line)
            ROI_normal_points.append(ROI_normal_line)
            cv2.rectangle(ROI_line_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.line(ROI_line_img, ROI_tangent_line[0], ROI_tangent_line[1], (0, 255, 0), 2)
            cv2.line(ROI_line_img, ROI_normal_line[0], ROI_normal_line[1], (255, 0, 0), 2)

        if show_tangentsandnormals:
            plt.imshow(ROI_line_img, cmap='gray')
            plt.show()

        # Automatically found lines in ROI.
        for t in range(len(ROI_normal_points)):
            ROI_prefix = "Automatic line " + str(t) + " in ROI " + str(box)
            ROI_resolution = Resolution(ROI_normal_points[t], thickness, img, point_scale_fit, line_length,
                                              pixel_over_realsize, sclbr_realsize_index, debug, print_info, output_dir)
            res_roi = ROI_resolution.getResolution(ROI_prefix)
            if res_roi != None:
                res_list.append(res_roi[0])
                r2_list.append(res_roi[1])
                name.append(ROI_prefix)
                x1_output.append(ROI_normal_points[t][0][0])
                y1_output.append(ROI_normal_points[t][0][1])
                x2_output.append(ROI_normal_points[t][1][0])
                y2_output.append(ROI_normal_points[t][1][1])

#############################################################
# Process outputs
#############################################################

# Write resolution values to spreadsheet.
output_spreadheet_path = str(output_dir) + "output.csv"
with open(output_spreadheet_path, mode='w', newline='') as csv_file:
    fieldnames = ['Line_Number', 'R_squared_value', 'Resolution', 'X1', 'Y1', 'X2', 'Y2']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(name)):
        writer.writerow({'Line_Number': name[i], 'R_squared_value': r2_list[i], 'Resolution': res_list[i],
                         'X1': x1_output[i], 'Y1': y1_output[i], 'X2': x2_output[i], 'Y2': y2_output[i]})


# Get corresponding thickness value in pixels.
thickness_in_pixels = []
if thickness == 1:
    thickness_in_pixels = 1
if thickness > 1:
    thickness_in_pixels = (thickness - 1) * 2 + 1


# Save a file with all parameters pertaining to the run.
info_file = open(str(output_dir) + "run_info.txt", "a")
info_file.write("Image used: " + str(image_path) + " \n")
if find_scalebar:
    info_file.write("Light threshold to find scalebar: " + str(light_threshold_setting) + " \n")
    info_file.write("Dark threshold to find scalebar: " + str(dark_threshold_setting) + " \n")
    info_file.write("Scalebar detected: " + str(sclbr_width) + " pixels = " + str(sclbr_realsize_num) + " " + str(sclbr_realsize_index) + " \n")
else:
    info_file.write("Scalebar width was set manually to: " + str(sclbr_width) + " pixels = " + str(sclbr_realsize_num) + " " + str(sclbr_realsize_index) + " \n")
info_file.write("Threshold to find contours: " + str(contour_threshold_setting) + " \n")
info_file.write("Automatic lines: " + str(not no_automatic) + " \n")
info_file.write("Maximum lines: " + str(max_lines) + " \n")
info_file.write("Line length: " + str(line_length) + " \n")
info_file.write("Thickness of lines used: " + str(thickness) + " (" + str(thickness_in_pixels) + " pixel(s) wide) \n")
info_file.write("Scale value to reduce points used in cuve fitting: " + str(point_scale_fit) + "(1 = use all points) \n")

if manual_option and manual_points != []:
    info_file.write("Manual lines option: " + str(len(manual_points)) + " lines run: \n")
    for i in range(len(manual_points)):
        info_file.write("\t Line " + str(i) + " from point 1: " + str(manual_points[i][0]) + ", to point 2: " + str(manual_points[i][1]) + " \n")
if manual_option and manual_ROIs != []:
    info_file.write("Manual ROI option: " + str(len(ROI_normal_points)) + " ROI's run: \n")
    for i in range(len(manual_ROIs)):
        x, y, w, h = manual_ROIs[i]
        info_file.write("\t Line " + str(i) + " from top left point: (" + str(x) + ", " + str(y) + "), width: " + str(w) + "px , height: " + str(h) + "px \n")

info_file.write("For replication of this run use: " + str(all_arguments))
info_file.close()