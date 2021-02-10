import cv2
import math as m
import numpy as np
from skimage.draw import line
from scipy.optimize import curve_fit
from statistics import mean
from matplotlib import pyplot as plt


# Get the contours for an image with a set threshold.
def getContours(image, low, high):
    grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded_img = cv2.threshold(grey_img, low, high, cv2.THRESH_BINARY)
    contour, _ = cv2.findContours(thresholded_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return contour, thresholded_img


class ContourSet:
    def __init__(self, contours, width, height):
        self.contours = contours
        self.width = width
        self.height = height
        self.area = width * height

    # Obtain index of the contour corresponding to the scalebar.
    def getScalebar(self):
        contour_widths = []
        for i in range(len(self.contours)):
            x, y, w, h = cv2.boundingRect(self.contours[i])
            # Only include contour widths with width < width of the image, and the height < 5% height of the image.
            if w < self.width and h < self.height / 20:
                contour_widths.append(w)
        # Get index of longest contour and the length of that contour.
        return contour_widths.index(max(contour_widths)), max(contour_widths)

    # Filter out small contours and parts touching sides of image.
    def filterSmallContours(self):
        new_prtcle_contours = []
        pointlist = []
        for c in self.contours:
            _, _, w, h = cv2.boundingRect(c)
            rect_area = w * h
            # Keep contours that area above the specified area.
            if self.area * 0.005 < rect_area:
                # For new contour object.
                new_prtcle_contours.append(c)
                # For getting contour pixels.
                pointlist.append(c.tolist())
        flat_pointlist = []
        for e1 in pointlist:
            for e2 in e1:
                for e3 in e2:
                    if e3[0] != 0 and e3[0] != self.width and e3[1] != 0 and e3[0] != self.height:
                        flat_pointlist.append(e3)
        return new_prtcle_contours, flat_pointlist


class PointPair:
    def __init__(self, point_1, point_2, scale):
        self.p1 = point_1
        self.p2 = point_2
        self.scale = scale

    def getscaledTangent(self):
        x1 = self.p1[0]
        y1 = self.p1[1]
        x2 = self.p2[0]
        y2 = self.p2[1]
        rise = y2 - y1
        run = x2 - x1
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        if rise == 0:
            nrise = 0
            nrun = self.scale
        if run == 0:
            nrise = self.scale
            nrun = 0
        else:
            theta = m.atan(rise / run)
            nrise = m.sin(theta) * self.scale
            nrun = m.cos(theta) * self.scale
        # outputs [(x1, y1), (x2, y2)]
        np1 = (int(cx + nrun), int(cy + nrise))
        np2 = (int(cx - nrun), int(cy - nrise))
        tangent_line = [np1, np2]
        return tangent_line

    def getnewNormal(self):
        tangent_line = self.getscaledTangent()
        x1, y1 = tangent_line[0]
        x2, y2 = tangent_line[1]
        rise = y2 - y1
        run = x2 - x1
        # outputs [(x1, y1), (x2, y2)]
        np1 = (int(x1 + run / 2 - rise / 2), int(y1 + rise / 2 + run / 2))
        np2 = (int(x1 + run / 2 + rise / 2), int(y1 + rise / 2 - run / 2))
        normal_line = [np1, np2]
        return normal_line


class LinePixels:
    def __init__(self, normal_line_points, thickness):
        self.normal_line_points = normal_line_points
        self.thickness = thickness

    # Get the pixels adjacent to the two points and retrieve the pixel locations for all lines and adjacent lines.
    def getAllPixels(self):
        x1 = self.normal_line_points[0][0]
        y1 = self.normal_line_points[0][1]
        x2 = self.normal_line_points[1][0]
        y2 = self.normal_line_points[1][1]
        final_line = [line(x1, y1, x2, y2)]
        for i in range(1, self.thickness):
            # line direction: /
            if x1 < x2 and y1 < y2 or x1 > x2 and y1 > y2:
                final_line.append(
                    line(x1 - self.thickness, y1 + self.thickness, x2 - self.thickness, y2 + self.thickness))
                final_line.append(
                    line(x1 + self.thickness, y1 - self.thickness, x2 + self.thickness, y2 - self.thickness))
            # line direction: \
            if x1 < x2 and y1 > y2 or x1 > x2 and y1 < y2:
                final_line.append(
                    line(x1 + self.thickness, y1 + self.thickness, x2 + self.thickness, y2 + self.thickness))
                final_line.append(
                    line(x1 - self.thickness, y1 - self.thickness, x2 - self.thickness, y2 - self.thickness))
            # line direction: |
            if x1 == x2:
                final_line.append(line(x1 + self.thickness, y1, x2 + self.thickness, y2))
                final_line.append(line(x1 - self.thickness, y1, x2 - self.thickness, y2))
            # line direction: -
            if y1 == y2:
                final_line.append(line(x1, y1 + self.thickness, x2, y2 + self.thickness))
                final_line.append(line(x1, y1 + self.thickness, x2, y2 + self.thickness))
        return final_line


class Intensity:
    def __init__(self, normal_line_points, thick, image):
        self.normal_line_points = normal_line_points
        self.thick = thick
        self.image = image
        self.pixel_object = LinePixels(normal_line_points, thick)

    # Get intensities for line profile, average profiles if thickness is > 1.
    def getLineIntensity(self):
        grey_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        height, width, _ = self.image.shape
        pixel_points_all = self.pixel_object.getAllPixels()
        line_profiles = []
        for adj_line in pixel_points_all:
            line_profile = []
            for p in range(len(adj_line[0])):
                xvalue = adj_line[0][p]
                yvalue = adj_line[1][p]
                # If the pixel point is within the bounds of the image bounds retrieve intensity.
                if 0 <= xvalue and xvalue < width and 0 <= yvalue and yvalue < height:
                    intensity = grey_img[yvalue, xvalue]
                    line_profile.append(intensity)
            line_profiles.append(line_profile)
        # print(line_profiles)
        # Get the smallest number of intensity values stored in adjacent lines.
        minimum = width * height * 100
        for x in range(len(line_profiles)):
            minimum = min(minimum, len(line_profiles[x]))
        # If thickness is > 1 then average the intensity values.
        if self.thick > 1:
            average_intensities = []
            for i in range(minimum):
                intensities_transect = []
                for t in range(self.thick):
                    intensities_transect.append(line_profiles[t][i])
                average_intensities.append(np.mean(intensities_transect))
        else:
            average_intensities = [item for sublist in line_profiles for item in sublist]
        return average_intensities


class Resolution:
    def __init__(self, normal_line_points, thick, image, point_scale_fit, line_length, pixel_over_realsize,
                 sclbr_realsize_index, debug, print_info, output_dir):
        self.normal_line_points = normal_line_points
        self.thick = thick
        self.image = image
        self.fitvalue = point_scale_fit
        self.line_length = line_length
        self.pixel_over_realsize = pixel_over_realsize
        self.sclbr_realsize_index = sclbr_realsize_index
        self.debug = debug
        self.print_info = print_info
        self.output_dir = output_dir

        self.intensity_object = Intensity(normal_line_points, thick, image)

    def getResolution(self, type):

        # Get y points for plotting the line profile.
        y_points = self.intensity_object.getLineIntensity()

        # If y_points is empty return none.
        if y_points == []:
            return None

        # Get corresponding x points for plotting the line profile.
        x_points = range(len(y_points))

        # Fit the profile data points to a sigmoid curve.
        p0 = [max(y_points), np.median(x_points), 1, min(y_points)]  # this is an mandatory initial guess
        # Perform a fit on 1/4 the points to increase speed.
        try:
            params, _ = curve_fit(sigmoid, x_points[0::self.fitvalue], y_points[0::self.fitvalue], p0, method='dogbox')
        except:
            if self.print_info:
                print(str(type) + " could not be fitted to a sigmoid curve.")
            return None

        # Produce x and y points of the fit line.
        points_in_fit = len(x_points)
        fit_x_points = np.linspace(0, points_in_fit, points_in_fit)
        fit_y_points = sigmoid(fit_x_points, *params)

        # Show plot with fit and data points.
        fig1 = plt.figure()
        plt.plot(x_points, y_points, 'o', label='data')
        plt.plot(fit_x_points, fit_y_points, label='fit')
        plt.legend(loc='best')
        plt.title("Intensity profile for " + str(type))
        plt.xlabel('Position on line axis')
        plt.ylabel('Intensity value')
        plt.close()
        if self.debug:
            plt.show()

        # Evaluate R^2 value to determine if the fit is acceptable.
        # residual sum of squares
        ss_res = np.sum((y_points - fit_y_points) ** 2)
        # total sum of squares
        ss_tot = np.sum((y_points - np.mean(y_points)) ** 2)
        # r-squared
        r2 = float(1 - (ss_res / ss_tot))
        # print("The R^2 value of the sigmoid fit for line " + str(l) + " is " + str(r2))

        # Only continue if r2 < 0.9.
        if r2 < 0.9:
            if self.print_info:
                print(str(type) + " had a poor r value of " + str(r2) + " and will be discarded.")
            return None

        # Get x cutoff for ceiling line.
        index = 0
        slope = getslope(fit_x_points[index], fit_x_points[index + 1], fit_y_points[index], fit_y_points[index + 1])
        while abs(slope) < 1:
            index += 1
            slope = getslope(fit_x_points[index], fit_x_points[index + 1], fit_y_points[index], fit_y_points[index + 1])
        # Convert index for fitted line to index for data points.
        ceiling_x_cutoff = int(index)
        if self.print_info:
            print(str(type) + " has as ceiling x cutoff of " + str(ceiling_x_cutoff))

        # Get x cutoff for floor line.
        lower_index = points_in_fit - 1
        slope = getslope(fit_x_points[lower_index], fit_x_points[lower_index - 1], fit_y_points[lower_index],
                         fit_y_points[lower_index - 1])
        while abs(slope) < 1:
            lower_index -= 1
            slope = getslope(fit_x_points[lower_index], fit_x_points[lower_index - 1], fit_y_points[lower_index],
                             fit_y_points[lower_index - 1])
        # Convert index for fitted line to index for data points.
        floor_x_cutoff = int(lower_index)
        if self.print_info:
            print(str(type) + " has as floor x cutoff of " + str(floor_x_cutoff))

        # Get ceiling average y values.
        ceiling_y_values = []
        for i in range(ceiling_x_cutoff):
            ceiling_y_values.append(float(y_points[i]))
        # If no y values are found, cancel: exception found, too much noise to produce good fit.
        if len(ceiling_y_values) == 0:
            if self.print_info:
                print("Exception occurred in the ceiling of " + str(type) + ", too much noise, line discarded.")
            return None
        ceiling_y = mean(ceiling_y_values)
        if self.print_info:
            print(str(type) + " has the average ceiling y value " + str(ceiling_y))

        # Get floor average y values.
        floor_y_values = []
        for i in range(floor_x_cutoff, len(x_points)):
            floor_y_values.append(float(y_points[i]))
        # If no y values are found, cancel: exception found, too much noise to produce good fit.
        if len(floor_y_values) == 0:
            if self.print_info:
                print("Exception occurred in the floor of " + str(type) + ", too much noise, line discarded.")
            return None
        floor_y = mean(floor_y_values)
        if self.print_info:
            print(str(type) + " has the average floor y value " + str(floor_y))

        # Get 25% and 75% bound x values with respect to the ceiling_y and floor_y values.
        if ceiling_y > floor_y:
            Y_25bound = abs(ceiling_y - floor_y) * 0.25 + floor_y
            Y_75bound = ceiling_y - abs(ceiling_y - floor_y) * 0.25
        else:
            Y_25bound = abs(ceiling_y - floor_y) * 0.25 + ceiling_y
            Y_75bound = floor_y - abs(ceiling_y - floor_y) * 0.25
        # print("The Y bounds for resolution calculation = bottom:" + str(Y_25bound) + ", top:" + str(Y_75bound))

        X_25bound = fit_x_points[find_nearest(fit_y_points, Y_25bound)]
        X_75bound = fit_x_points[find_nearest(fit_y_points, Y_75bound)]
        if self.print_info:
            print(str(type) + " bounds for resolution calculation: 25% Y=" + str(X_25bound) + "and 75% Y=" + str(
                X_75bound))

        resolution_pixels = abs(X_75bound - X_25bound)

        # Scale resolution to real value.
        resolution = resolution_pixels * self.pixel_over_realsize

        if self.print_info:
            print("Resolution of " + str(type) + " is = " + str(resolution) + " " + str(self.sclbr_realsize_index))

        # Show plot with fit and data points.
        fig1.savefig(str(self.output_dir) + str(type) + ".jpg", dpi=fig1.dpi)


        # Show where the bounds are placed
        fig2 = plt.figure()
        plt.plot(x_points, y_points, 'o', label='data')
        plt.plot([ceiling_x_cutoff, ceiling_x_cutoff], [0, max(y_points)], label='upper bound')
        plt.plot([floor_x_cutoff, floor_x_cutoff], [0, max(y_points)], label='lower bound')
        plt.plot([ceiling_x_cutoff, max(x_points)], [floor_y, floor_y], label='ceiling')
        plt.plot([floor_x_cutoff, min(x_points)], [ceiling_y, ceiling_y], label='floor')
        plt.plot(fit_x_points, fit_y_points, label='fit')
        plt.xlabel('Position on line axis')
        plt.ylabel('Intensity value')
        plt.title("Intensity profile for " + str(type))
        plt.legend(loc='best')
        fig2.savefig(str(self.output_dir) + str(type) + " bounding lines.jpg", dpi=fig2.dpi)
        plt.close()
        if self.debug:
            plt.show()

        # Show img where the normal chosen is shown in red.
        img_oneline = self.image.copy()
        cv2.line(img_oneline, self.normal_line_points[0], self.normal_line_points[1], (255, 0, 0), 3)
        cv2.imwrite(str(self.output_dir) + str(type) + " normal.jpg", img_oneline)
        if self.debug:
            plt.imshow(img_oneline, cmap='gray')
            plt.show()

        output = (resolution, r2)
        return output


# Find index of value in array closest to a set value.
def find_nearest(array, value):
    idx = np.abs(array - value).argmin()
    return idx


# Fit the profile data points to a sigmoid curve.
def sigmoid(x, L, x0, k, b):
    y = (L / (1 + np.exp(k * (x - x0)))) + b
    return (y)


# Get slope across points in the fitted line.
def getslope(x1, x2, y1, y2):
    rise = y2 - y1
    run = x2 - x1
    return (rise / run)


class Spreadsheet:
    def __init__(self, dataframe):
        self.df = dataframe

    def import_all_manual_data(self):
        line = []
        box = []
        for i in range(len(self.df)):
            x1 = int(self.df['X1'][i])
            y1 = int(self.df['Y1'][i])
            x2 = int(self.df['X2'][i])
            y2 = int(self.df['Y2'][i])
            if self.df['Type'][i] == "line":
                line.append([(x1, y1), (x2, y2)])
            if self.df['Type'][i] == "rectangle":
                w = x2 - x1
                h = y2 - y1
                box.append([x1, y1, w, h])
        return line, box
