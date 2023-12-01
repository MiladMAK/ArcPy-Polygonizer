import arcpy

# Set up workspace and environment settings
arcpy.env.workspace = r"G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(2277)  # NAD 1983 StatePlane Texas Central (US Feet)
arcpy.env.overwriteOutput = True  # To overwrite existing feature classes

# Replace 'street_layer' with the actual path to your street layer
street_layer = "G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb\CTNTest_1"

# Predefine buffer distances based on street level
buffer_distances = {
    1: 40,  # Level 1 streets
    2: 40,  # Level 2 streets
    3: 50,  # Level 3 streets
    4: 75   # Level 4 streets
}

# Create a feature class for the final output polygons
output_fc = arcpy.CreateFeatureclass_management(
    arcpy.env.workspace, "FinalPolygons", "POLYGON",
    spatial_reference=arcpy.env.outputCoordinateSystem
)

# Add fields to the output feature class as needed
arcpy.AddField_management(output_fc, "STREET_NAME", "TEXT")
arcpy.AddField_management(output_fc, "STREET_LEVEL", "SHORT")

try:
    # Loop through street segments to create segmented buffers and intermediate segments
    with arcpy.da.SearchCursor(street_layer, ["SHAPE@", "STREET_NAME", "STREET_LEVEL"]) as cursor:
        for row in cursor:
            geometry = row[0]
            street_name = row[1]
            street_level = row[2]

            BUFFER_DISTANCE = buffer_distances.get(street_level, 0)

            if BUFFER_DISTANCE == 0:
                continue  # Skip segments with an unknown street level

            buffered_geometry = arcpy.Polygon(arcpy.Array([geometry.buffer(BUFFER_DISTANCE).getPart(0)]),
                                              arcpy.env.outputCoordinateSystem)

            with arcpy.da.InsertCursor(output_fc, ["SHAPE@", "STREET_NAME", "STREET_LEVEL"]) as insert_cursor:
                insert_cursor.insertRow([buffered_geometry, street_name, street_level])

    print("Final Polygons created.")

except Exception as e:
    print(f"An error occurred: {str(e)}")
