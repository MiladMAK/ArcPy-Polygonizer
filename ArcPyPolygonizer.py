import arcpy
from arcpy import env

# Set up workspace and environment settings
env.workspace = r"G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb"
env.outputCoordinateSystem = arcpy.SpatialReference(2277)  # NAD 1983 StatePlane Texas Central (US Feet)
arcpy.env.overwriteOutput = True  # to rewrite the feature

# Replace 'street_layer' with the actual path to your street layer
street_layer = "G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb\CTNTest_1"
intersection_layer = "G:\ATD\ACTIVE TRANS\Vision Zero\GIS\Polygon Update\Polygon Update\Default.gdb\IntersectionsTest_1"

# Predefine buffer distances based on street level
buffer_distances = {
    1: 40,  # Level 1 streets
    2: 40,  # Level 2 streets
    3: 50,  # Level 3 streets
    4: 75  # Level 4 streets
}

# Create a feature class for segmented buffers
buffer_fc = arcpy.CreateFeatureclass_management(
    env.workspace, "SegmentedBuffers", "POLYGON",
    spatial_reference=env.outputCoordinateSystem
)

# Add fields to the buffer feature class as needed
arcpy.AddField_management(buffer_fc, "STREET_NAME", "TEXT")
arcpy.AddField_management(buffer_fc, "STREET_LEVEL", "SHORT")

# Create a feature class for intermediate segments
intermediate_fc = arcpy.CreateFeatureclass_management(
    env.workspace, "IntermediateSegments", "POLYGON",
    spatial_reference=env.outputCoordinateSystem
)

# Add fields to the intermediate feature class as needed
arcpy.AddField_management(intermediate_fc, "STREET_NAME", "TEXT")
arcpy.AddField_management(intermediate_fc, "STREET_LEVEL", "SHORT")
arcpy.AddField_management(intermediate_fc, "SHAPE_LENGTH", "DOUBLE")  # Add SHAPE_LENGTH field
arcpy.AddField_management(intermediate_fc, "SHAPE_AREA", "DOUBLE")    # Add SHAPE_AREA field

# Track processed segments
processed_segments = {}

# Define the desired spatial reference
desired_spatial_reference = env.outputCoordinateSystem

# Create a dictionary to store polygon geometries at intersections
intersection_polygons = {}

# Loop through street segments to create segmented buffers and intermediate segments
with arcpy.da.SearchCursor(street_layer, ["SHAPE@", "STREET_NAME", "STREET_LEVEL", "OBJECTID"]) as cursor:
    for row in cursor:
        geometry = row[0]
        street_name = row[1]
        street_level = row[2]
        object_id = row[3]

        # Define buffer distance based on street level
        BUFFER_DISTANCE = buffer_distances.get(street_level, 0)

        if BUFFER_DISTANCE == 0:
            continue  # Skip segments with an unknown street level

        # Create a new geometry with the desired spatial reference
        buffered_geometry = arcpy.Polygon(arcpy.Array([geometry.buffer(BUFFER_DISTANCE).getPart(0)]),
                                          desired_spatial_reference)

        # Append the segmented buffer to the feature class
        with arcpy.da.InsertCursor(buffer_fc, ["SHAPE@", "STREET_NAME", "STREET_LEVEL"]) as insert_cursor:
            insert_cursor.insertRow([buffered_geometry, street_name, street_level])

        # Create intermediate segments
        remaining_length = geometry.length - 2 * BUFFER_DISTANCE
        ideal_segment_length = 150 if street_level in [1, 2] else 250

        if remaining_length > 0:
            num_segments = int(remaining_length / ideal_segment_length)
            if num_segments > 0:
                segment_length = remaining_length / num_segments
                for i in range(num_segments):
                    start_distance = BUFFER_DISTANCE + i * segment_length
                    end_distance = start_distance + segment_length
                    intermediate_geometry = arcpy.Polygon(
                        arcpy.Array([geometry.positionAlongLine(start_distance, True).firstPoint,
                                     geometry.positionAlongLine(end_distance, True).firstPoint,
                                     geometry.positionAlongLine(end_distance, True).lastPoint,
                                     geometry.positionAlongLine(start_distance, True).lastPoint]),
                        desired_spatial_reference
                    )

                    # Calculate shape length and shape area for the intermediate segment
                    intermediate_geometry = intermediate_geometry.projectAs(desired_spatial_reference)  # Project to the desired spatial reference
                    shape_length = intermediate_geometry.length
                    shape_area = intermediate_geometry.area

                    # Append the intermediate segment to the feature class
                    with arcpy.da.InsertCursor(intermediate_fc, ["SHAPE@", "STREET_NAME", "STREET_LEVEL", "SHAPE_LENGTH", "SHAPE_AREA"]) as insert_cursor:
                        insert_cursor.insertRow([intermediate_geometry, street_name, street_level, shape_length, shape_area])

                    # Debugging statement
                    arcpy.AddMessage(f"Intermediate Segment Created: Street Name: {street_name}, Segment Length: {shape_length}, Segment Area: {shape_area}")

        # Mark the street segment as processed
        processed_segments[object_id] = True

# Create polygons for the remaining intersection areas
for object_id, intersection_geometry in intersection_polygons.items():
    with arcpy.da.InsertCursor(buffer_fc, ["SHAPE@", "STREET_NAME", "STREET_LEVEL"]) as insert_cursor:
        insert_cursor.insertRow([intersection_geometry, street_name, street_level])

print("IntermediateSegments and Intersection Polygons created.")
