# ArcPy-Polygonizer
This is an attempt to replicate the QGIS plug-in called Polygonizer created by **Frank Hereford** at City of Austin Transportation and Public Works Department
# Background from the QGIS plugin Repository
The Vision Zero team, as part of the Austin Transportation and Public Works Department, operates a database of crashes in and around the Austin city limits. These's crashes are tracked by a point position, and in an effort to conduct analysis of the city's roadways in relation to crash location and crash severity, a set of polygons was created based on the street network. These polygons are of approximate equal area and have are formed in such a way that intersections are built into a single shape and interconnecting roads between intersections are divided into equal segments. By aggregating crashes into these polygons, comparisons become possible between intersections and road segments.
# Background 2
A working QGIS plugin (https://github.com/frankhereford/qgis-polygonizer)https://github.com/frankhereford/qgis-polygonizer) has successfully fulfilled the purpose of this algorithm. However, due to the relative slow processing and multiple platforms involved (QGIS, AGOL, ArcPro) and the complexity I thought it might be useful to **make an algorithm that can do the job directly inside ArcPro**.
# The QGIS Plugin Workflow
To create and correct polygons at any ASMP level (https://austin.maps.arcgis.com/apps/webappviewer/index.html?id=2a3c539da76b4f49906a3524ed4a2cc9) the workflow comprises:
1- Preparing a reference street network in QGIS (calling CTN (https://austin.maps.arcgis.com/apps/mapviewer/index.html?layers=52347b99aba448e0a7e5d4b9a5cb09f9&layerId=0) layer through AGOL)
2- Running the plugin which has sliders to choose the width, length and segment length
3- Edit the created polygons inside QGIS
4- Transfer the polygons (e.g., as a shapefile) to ArcPro 
5- Push the new sets of polygons (created or corrected) to the maint database inside **ATD_ADMIN.vision_zero_polygons**

Multiple drawbacks are faced 
