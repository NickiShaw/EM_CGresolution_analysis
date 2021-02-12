setOption("ExpandableArrays", true);

n = roiManager("count");

ROI_type = newArray;
x1 = newArray;
y1 = newArray;
x2 = newArray;
y2 = newArray;
for (i=0; i<n; i++) {
	roiManager("select", i);
	type = Roi.getType();
	ROI_type[i] = type;
	if (type == "rectangle"){
		getSelectionBounds(x, y, width, height);
		x1[i] = x;
		y1[i] = y;
		x2[i] = x + width;
		y2[i] = y + height;
	} if (type == "line"){
		Roi.getCoordinates(xpoints, ypoints);
		x1[i] = xpoints[0];
		y1[i] = ypoints[0];
		x2[i] = xpoints[1];
		y2[i] = ypoints[1];
	}
}


// add new table.
Table.create("Point coordinates");
// set columns.
Table.setColumn("Type", ROI_type);
Table.setColumn("X1", x1);
Table.setColumn("Y1", y1);
Table.setColumn("X2", x2);
Table.setColumn("Y2", y2);
