# ArcPy-Polygonizer
This is an attempt to replicate the QGIS plug-in called Polygonizer created by **Frank Hereford** at the City of Austin Transportation and Public Works Department
# Background from the QGIS plugin Repository 
As part of the Austin Transportation and Public Works Department, the Vision Zero team operates a database of crashes in and around the Austin city limits. A point position tracks these crashes, and to analyze the city's roadways about crash location and crash severity, a set of polygons was created based on the street network. These polygons are of approximately equal area and are formed so that intersections are built into a single shape, and interconnecting roads between intersections are divided into equal segments. By aggregating crashes into these polygons, comparisons between intersections and road segments become possible.
# Background 2
A working QGIS plugin (https://github.com/frankhereford/qgis-polygonizer) has successfully fulfilled the purpose of this algorithm. However, due to the relatively slow processing and multiple platforms involved (QGIS, AGOL, ArcPro) and the complexity, it is useful to make an algorithm that can do the job directly inside ArcPro**.
# The QGIS Plugin Workflow
To create and correct polygons at any ASMP level (https://austin.maps.arcgis.com/apps/webappviewer/index.html?id=2a3c539da76b4f49906a3524ed4a2cc9) the workflow comprises:
1- Preparing a reference street network in QGIS (calling CTN (https://austin.maps.arcgis.com/apps/mapviewer/index.html?layers=52347b99aba448e0a7e5d4b9a5cb09f9&layerId=0) layer through AGOL)
2- Select (active selection by drawing a rectangle around the chosen streets) the chosen streets
3- Running the plugin, which has sliders to choose the width, length, and segment length
4- Edit the created polygons inside QGIS
5- Transfer the polygons (e.g., as a shapefile) to ArcPro 
6- Push the new sets of polygons (created or corrected) to the maint database inside **ATD_ADMIN.vision_zero_polygons**

 # Problem
Multiple shortcomings might occur while using the QGIS plugin, which can be solved with some workarounds. However, this might not be quickly achievable for a non-experienced analyst. Having a tool inside ArcPro can provide a faster solution and a quicker switch between editing polygons and creating them from scratch.

# Proposed solution through ArcPy Polygonizer
