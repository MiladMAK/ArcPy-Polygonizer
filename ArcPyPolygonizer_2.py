import arcpy
from arcpy import env

# Set up workspace and environment settings
env.workspace = r"G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb"
env.outputCoordinateSystem = arcpy.SpatialReference(2277)  # NAD 1983 StatePlane Texas Central (US Feet)
arcpy.env.overwriteOutput = True  # To overwrite existing feature classes

# Replace 'street_layer' with the actual path to your street layer
street_layer = "G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb\CTNTest_1"
intersection_layer = "G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb\IntersectionsTest_1"

# Predefine buffer distances based on street level
buffer_distances = {
    1: 40,  # Level 1 streets
    2: 40,  # Level 2 streets
    3: 50,  # Level 3 streets
    4: 75   # Level 4 streets
}

# Create a feature class for segmented buffers
buffer_fc = arcpy.CreateFeatureclass_management(
    env.workspace, "SegmentedBuffers", "POLYGON",
    spatial_reference=env.outputCoordinateSystem
)

# Add fields to the buffer feature class as needed
arcpy.AddField_management(buffer_fc, "STREET_NAME", "TEXT")
arcpy.AddField_management(buffer_fc, "STREET_LEVEL", "SHORT")

# Create a feature class for intersection polygons (supporting multipart geometries)
intersection_fc = arcpy.CreateFeatureclass_management(
    out_path=env.workspace,
    out_name="IntersectionPolygons",
    geometry_type="POLYGON",
    spatial_reference=env.outputCoordinateSystem,
    has_m="DISABLED",
    has_z="DISABLED"
)

# Add fields to the intersection feature class as needed
arcpy.AddField_management(intersection_fc, "STREET_NAME", "TEXT")
arcpy.AddField_management(intersection_fc, "STREET_LEVEL", "SHORT")
arcpy.AddField_management(intersection_fc, "INTERSECTIONID", "TEXT")

# Perform a spatial join between intersection points and street layer
arcpy.analysis.SpatialJoin(
    target_features=intersection_layer,
    join_features=street_layer,
    out_feature_class="JoinedIntersections",
    join_type="KEEP_COMMON",
    match_option="CLOSEST",
    search_radius="50 Feet"  # Adjust the search radius as needed
)

# Update the cursor to use the joined layer
joined_layer = "JoinedIntersections"

# Define the desired spatial reference
desired_spatial_reference = env.outputCoordinateSystem

# Loop through the joined layer to create intersection polygons
with arcpy.da.SearchCursor(joined_layer, ["SHAPE@", "STREET_NAME", "STREET_LEVEL", "X", "Y"]) as cursor:
    for row in cursor:
        intersection_geometry = row[0]
        street_name = row[1]
        street_level = row[2]
        x_coord = row[3]
        y_coord = row[4]

        # Create a unique identifier based on X and Y coordinates
        intersection_id = f"{x_coord}_{y_coord}"

        # Check if the geometry is multipart
        if intersection_geometry.isMultipart:
            # Split the multipart geometry into single-part geometries
            parts = intersection_geometry.getPart()
            for part in parts:
                # Create a new single-part geometry with the desired spatial reference
                single_part_geometry = arcpy.Polygon(part, desired_spatial_reference)
                
                # Insert each single-part geometry separately
                with arcpy.da.InsertCursor(intersection_fc, ["SHAPE@", "INTERSECTIONID", "STREET_NAME", "STREET_LEVEL" ]) as insert_cursor:
                    insert_cursor.insertRow([single_part_geometry, intersection_id, street_name, street_level])
        else:
            # If the geometry is already single-part, insert it as is
            single_part_geometry = arcpy.Polygon(intersection_geometry.getPart(0), desired_spatial_reference)
            with arcpy.da.InsertCursor(intersection_fc, ["SHAPE@", "INTERSECTIONID", "STREET_NAME", "STREET_LEVEL"]) as insert_cursor:
                insert_cursor.insertRow([single_part_geometry, intersection_id, street_name, street_level])


# Calculate shape_length and shape_area for IntersectionPolygons
# Calculate shape_length and shape_area for IntersectionPolygons
#arcpy.management.CalculateField(intersection_fc, "SHAPE@LENGTH", "!SHAPE!.length", "PYTHON3")
#arcpy.management.CalculateField(intersection_fc, "SHAPE@AREA", "!SHAPE!.area", "PYTHON3")
# Loop through street segments to create segmented buffers and intermediate segments

with arcpy.da.SearchCursor(street_layer, ["SHAPE@", "OBJECTID"]) as cursor:
    for row in cursor:
        geometry = row[0]
        object_id = row[1]

        # Define buffer distance based on street level (you may need to join with street info)
        street_level = 1  # Replace with the appropriate logic to determine street level

        BUFFER_DISTANCE = buffer_distances.get(street_level, 0)

        if BUFFER_DISTANCE == 0:
            continue  # Skip segments with an unknown street level

        # Create a new geometry with the desired spatial reference
        buffered_geometry = arcpy.Polygon(arcpy.Array([geometry.buffer(BUFFER_DISTANCE).getPart(0)]),
                                          desired_spatial_reference)

        # Append the segmented buffer to the feature class
        with arcpy.da.InsertCursor(buffer_fc, ["SHAPE@", "STREET_NAME", "STREET_LEVEL"]) as insert_cursor:
            insert_cursor.insertRow([buffered_geometry, None, street_level])  # Street name is not available

print("IntermediateSegments and Intersection Polygons created.")
