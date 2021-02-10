
import cv2
from matplotlib import pyplot as plt
import sys
from PIL import Image
import math as m
import numpy as np
import pandas as pd
from Image_features_v2 import *
import datetime
import csv
import os

# for arg in sys.argv:
#     print(arg)
all_arguments = "flags and stuff"


show_scalebar = False
show_contour_threshold = False
show_contours = False
show_tangentsandnormals = False


image_path = "C:\\Users\\shawn\\Desktop\\W2021_coop\\resolution\\Gold_nanoparticles.jpg"
manual_path = "C:\\Users\\shawn\\Desktop\\W2021_coop\\resolution\\Point coordinates of Gold Nanoparticles.csv"
output_dir = "C:\\Users\\shawn\\Desktop\\W2021_coop\\resolution\\output"

# Make folder for each individual run to avoid overwriting previous output.
time = str(datetime.datetime.now()).replace(" ", "_").replace(":", "-")
output_dir = output_dir + "\\" + time + "\\"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

img = cv2.imread(image_path)

# Get dimensions of image.
img_height, img_width, _ = img.shape
img_area = img_height * img_width

#############################################################
# Get scalebar
#############################################################
scbr_img = img.copy()

# Get contours for light and dark thresholds.
lightcontour, _ = getContours(scbr_img, 50, 255)
darkcontour, _ = getContours(scbr_img, 220, 255)

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

# Draw contours to show scalebar was located.
if show_scalebar:
    print("The scalebar is " + str(sclbr_width) + " px long.")
    cv2.drawContours(scbr_img, cnts, ix, (255, 0, 0), 1)
    plt.imshow(scbr_img, cmap='gray')
    plt.show()

#############################################################
# Analyse scalebar text
#############################################################
sclbr_realsize_num = 50
sclbr_realsize_index = 'nm'

pixel_over_realsize = sclbr_realsize_num / sclbr_width

#############################################################
# Get resolution using CG method
#############################################################
prtcle_img = img.copy()

# Apply threshold for finding all particle contours.
prtcle_contours, threshold_img = getContours(prtcle_img, 140, 255)

if show_contour_threshold:
    plt.imshow(threshold_img, cmap='gray')
    plt.show()

# Filter out small contours (noise) and parts touching the edges of the image.
particle_contours = ContourSet(prtcle_contours, img_width, img_height)
filtered_contours, contour_points = particle_contours.filterSmallContours()

# Draw particle contours.
if show_contours:
    cv2.drawContours(prtcle_img, filtered_contours, -1, (255, 0, 0), 2)
    plt.imshow(prtcle_img, cmap='gray')
    plt.show()

# Half the number of points until there are less than 1000
while (len(contour_points) > 900):
    contour_points = contour_points[1::2]

# Round the length of the contour list down to an even number (so each point makes a pair for line drawing).
even_number = m.floor(len(contour_points) / 2) * 2

# Set line widths for profile.
line_length = img_width * 0.03

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

resolutions = []
passed = []
failed = []
debug = False
print_info = False
point_scale_fit = 5
manual_lines = True
ROI_included = True

res_list = []
r2_list = []
name = []
x1_output = []
y1_output = []
x2_output = []
y2_output = []
thickness = 1

# Automatically found lines.
for t in range(10):
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

if manual_lines or ROI_included:
    manual_df = Spreadsheet(pd.read_csv(manual_path, dtype=str))

# Manually set lines
if manual_lines:
    manu_res = []
    manu_r2 = []
    manu_i = []
    manual_points = manual_df.import_all_manual_data()[0]
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
            x1_output.append(normal_points[t][0][0])
            y1_output.append(normal_points[t][0][1])
            x2_output.append(normal_points[t][1][0])
            y2_output.append(normal_points[t][1][1])
        # For manually set lines show if the selection failed.
        else:
            res_list.append("failed")
            r2_list.append("failed")
            name.append(manual_prefix)

# Automatic lines from ROI.
if ROI_included:
    manual_ROIs = manual_df.import_all_manual_data()[1]
    for box in manual_ROIs:
        x, y, w, h = box
        # Crop the image to the ROI.
        ROI = img[y:y+h, x:x+w]

        # Apply threshold for finding all particle contours.
        ROI_prtcle_contours, ROI_threshold_img = getContours(ROI, 140, 255)

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
        while (len(ROI_contour_points) > 900):
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
            ROI_tangent_points.append(ROI_tangent_line)
            ROI_normal_points.append(ROI_normal_line)
            cv2.rectangle(ROI_line_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.line(ROI_line_img, ROI_tangent_line[0], ROI_tangent_line[1], (0, 255, 0), 2)
            cv2.line(ROI_line_img, ROI_normal_line[0], ROI_normal_line[1], (255, 0, 0), 2)

        if show_tangentsandnormals:
            plt.imshow(ROI_line_img, cmap='gray')
            plt.show()

        # Automatically found lines in ROI.
        for t in [83,84,85]:#range(len(ROI_normal_points)):
            ROI_prefix = "Automatic line " + str(t) + " in ROI " + str(box)
            ROI_resolution = Resolution(ROI_normal_points[t], thickness, img, point_scale_fit, line_length,
                                              pixel_over_realsize, sclbr_realsize_index, debug, print_info, output_dir)
            res_roi = ROI_resolution.getResolution(ROI_prefix)
            if res_roi != None:
                print("passed")
                res_list.append(res_roi[0])
                r2_list.append(res_roi[1])
                name.append(ROI_prefix)
                x1_output.append(normal_points[t][0][0])
                y1_output.append(normal_points[t][0][1])
                x2_output.append(normal_points[t][1][0])
                y2_output.append(normal_points[t][1][1])

print(len(name), len(r2_list), len(res_list), len(x1_output), len(y1_output))

# Write resolution values to spreadsheet.
output_spreadheet_path = str(output_dir) + "output.csv"
with open(output_spreadheet_path, mode='w', newline='') as csv_file:
    fieldnames = ['Line_Number', 'R_squared_value', 'Resolution', 'X1', 'Y1', 'X2', 'Y2']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(len(name)):
        writer.writerow({'Line_Number': name[i], 'R_squared_value': r2_list[i], 'Resolution': res_list[i],
                         'X1': x1_output[i], 'Y1': y1_output[i], 'X2': x2_output[i], 'Y2': y2_output[i]})



manual_lines = True
ROI_included = True

# Save a file with all parameters pertaining to the run.
info_file = open(str(output_dir) + "run_info.txt", "a")
info_file.write("Image used: " + str(image_path) + " \n")

if manual_lines:
    info_file.write("Manual lines option : " + str(len(manual_points)) + " lines run: \n")
    for i in range(len(manual_points)):
        info_file.write("\t Line " + str(i) + " from point 1: " + str(manual_points[i][0]) + ", to point 2: " + str(manual_points[i][0]) + " \n")
if ROI_included:
    info_file.write("Manual ROI option : " + str(len(manual_ROIs)) + " ROI's run: \n")
    for i in range(len(manual_ROIs)):
        info_file.write("\t Line " + str(i) + " from top left: " + str(manual_ROIs[i][0]) + ", to bottom right: " + str(manual_ROIs[i][0]) + " \n")

info_file.write("For replication of this run use: " + str(all_arguments))
info_file.close()