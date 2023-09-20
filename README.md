# ArcPy-Polygonizer
This attempts to replicate the QGIS plug-in called Polygonizer created by **Frank Hereford** at the City of Austin Transportation and Public Works Department. The two attempts (ArcPyPolygonizer) differ in some details but have the same structure.
# Background from the QGIS plugin Repository 
As part of the Austin Transportation and Public Works Department, the Vision Zero team operates a database of crashes in and around the Austin city limits. A point position tracks these crashes, and to analyze the city's roadways about crash location and crash severity, a set of polygons was created based on the street network. These polygons are of approximately equal area and are formed so that intersections are built into a single shape, and interconnecting roads between intersections are divided into equal segments. Aggregating crashes into these polygons makes comparisons between intersections and road segments possible.
![image](https://github.com/MiladMAK/ArcPy-Polygonizer/assets/134707080/7754d195-e970-4cea-8100-b7dea01b473e)

# Background 2
A working QGIS plugin (https://github.com/frankhereford/qgis-polygonizer) has successfully fulfilled the purpose of this algorithm. However, due to the relatively slow processing and multiple platforms involved (QGIS, AGOL, ArcPro) and the complexity, it is useful to make an algorithm that can do the job directly inside ArcPro.
# The QGIS Plugin Workflow
To create and correct polygons at any ASMP level (https://austin.maps.arcgis.com/apps/webappviewer/index.html?id=2a3c539da76b4f49906a3524ed4a2cc9) the workflow comprises:
1- Preparing a reference street network in QGIS (calling CTN (https://austin.maps.arcgis.com/apps/mapviewer/index.html?layers=52347b99aba448e0a7e5d4b9a5cb09f9&layerId=0) layer through AGOL)
2- Select (active selection by drawing a rectangle around the chosen streets) the chosen streets
3- Running the plugin, which has sliders to choose the width, length, and segment length
4- Edit the created polygons inside QGIS
5- Transfer the polygons (e.g., as a shapefile) to ArcPro 
6- Push the new sets of polygons (created or corrected) to the "maint" database inside **ATD_ADMIN.vision_zero_polygons**

 # Problem
Multiple shortcomings might occur while using the QGIS plugin, which can be solved with some workarounds. However, this might not be quickly achievable for a non-experienced analyst. A tool inside ArcPro can provide a faster solution and a quicker switch between editing polygons and creating them from scratch.

# Proposed solution through ArcPy Polygonizer
These proposed algorithms, upon being completed, can be converted to tools in ArcPro where the user needs only to provide the street network and intersection layers. The rest will be taken care of through the program.

# Algorithm 
ArcPy Polygonizer is created following the documentation at https://atd-dts.gitbook.io/atd-geospatial/miscelaneous/vision-zero-polygon-maintenance.


# Process
Creating buffers first and then creating intermediate sections can be a valid approach, and it may sometimes simplify the logic. However, whether it's better to create buffers before or after creating intermediate sections depends on your project's specific requirements and constraints.

Here are some considerations for both approaches:

# Creating Buffers First:

Simpler Logic: This approach can be simpler to implement because you create buffers for all street segments first, then focus on identifying intersections and creating intermediate sections.

Full Coverage: It ensures complete buffer coverage for all street segments, which can be useful if you need to analyze or visualize the buffer areas independently.

Flexibility: You can perform additional analyses on the buffered segments before creating intermediate sections.

# Creating Intermediate Sections First:

Efficiency: If your primary goal is to identify and represent the intersections where buffered segments meet, creating intermediate sections first might be more efficient, as you only generate polygons where necessary.

Reduces Data Volume: It can reduce the data volume because you don't need to store buffers for all street segments, only for the segments that contribute to intersections.

Complex Intersections: If your dataset contains complex intersections with multiple street segments converging, creating intermediate sections first can help you capture the exact geometry of those intersections.

Choosing these approaches often depends on your project's specific requirements and constraints. Creating intermediate sections first can be a good strategy if your project primarily focuses on the intersections. However, creating buffers first may be preferable if you need buffers for other purposes or want to maintain a complete buffer coverage.

Ultimately, the decision should align with the goals of your project and how you plan to use the resulting spatial data.

# Sample data:

The sample data on which the code is tested is as follows. 

![image](https://github.com/MiladMAK/ArcPy-Polygonizer/assets/134707080/d272105b-36aa-4933-94e7-6b796e54b241)

The sample data comprises a line segment extracted from CTN and a point dataset extracted from intersections between line segments.

# Current status:
The algorithm (2 of them, and the second one is more sophisticated) works, but there are a series of problems. Some of the most important problems are explained after the picture:
![image](https://github.com/MiladMAK/ArcPy-Polygonizer/assets/134707080/94b9f8cc-ebe2-47f6-98a8-fb717e2b7b10)


- [ ] The segmented polygons are created but not split beyond the intersection points. For example, if a line segment does not encounter an intersection (a point coming from the intersection layer), the polygon will continue along the entire section.
- [ ] The intersection polygons are not created. While we have an initial point of starting with segmented polygons, there are no intersection polygons.
- [ ] No shape-length and shape-area inside the IntersectionPolygons layer are all set to 0.

# Code break-down:
1. Import ArcPy and Set Environment Variables:

The script starts by importing the arcpy module, which provides access to ArcGIS geospatial functionality.
It also imports the env module from arcpy.
The env.workspace variable is set to specify the geodatabase location where the operations will be performed.
The env.outputCoordinateSystem variable is set to specify the coordinate system for the output data.
arcpy.env.overwriteOutput is set to True, allowing the script to overwrite existing feature classes if they have the same name.

2. Define Input Data Paths:

street_layer and intersection_layer variables are set to specify the paths to two feature classes within the geodatabase. These feature classes represent street data and intersection data, respectively.

3. Define Buffer Distances:

The buffer_distances dictionary is defined, associating buffer distances with street levels.

4. Create Feature Classes:

Two new empty feature classes are created using arcpy.CreateFeatureclass_management. One is for segmented buffers (buffer_fc), and the other is for intersection polygons (intersection_fc). These feature classes will store the results of the operations.

5. Add Fields to Feature Classes:

Fields are added to both the buffer_fc and intersection_fc feature classes using arcpy.AddField_management. These fields include "STREET_NAME," "STREET_LEVEL," and "INTERSECTIONID."

6. Spatial Join:

The arcpy.analysis.SpatialJoin function is used to perform a spatial join operation between the intersection points and street layer. The result is stored in a new feature class called "JoinedIntersections."

7. Loop Through Joined Data:

A for loop iterates through the records in the "JoinedIntersections" feature class.
For each record, it extracts relevant information such as geometry, street name, street level, and coordinates.
It generates a unique intersection_id based on X and Y coordinates.
If the geometry is multipart (e.g., an intersection with multiple parts), it splits it into single-part geometries and inserts them separately into the intersection_fc.
If the geometry is already single-part, it inserts it as is into the intersection_fc.

8. Calculate Shape Length and Shape Area:

The script includes a commented-out code that calculates the shape length and shape area for the intersection polygons. However, this code is currently disabled (commented out).

9. Loop Through Street Segments:

Another for loop iterates through the street segments in the "street_layer" feature class.
For each segment, it calculates a buffered geometry based on the street level and appends it to the "buffer_fc" feature class.

Print a Message:

The script concludes by printing "IntermediateSegments and Intersection Polygons created."
