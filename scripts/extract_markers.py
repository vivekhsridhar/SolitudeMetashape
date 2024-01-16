import numpy as np
import pandas as pd
import Metashape

def list_coordinates(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')[1:-1]
            # Filter out empty strings before converting to float
            values = [float(val) if val else 0.0 for val in values]
            data.append(tuple(values))
    return data

def process_chunk(chunk, global_coordinates):
    T = chunk.transform.matrix

    data_list = []

    for point_idx, global_coord in enumerate(global_coordinates):
        p = T.inv().mulp(chunk.crs.unproject(Metashape.Vector(global_coord)))
        print(f"Image pixel coordinates of point {point_idx + 1} with global coordinates ({chunk.crs.name}): {global_coord}")

        for i, camera in enumerate(chunk.cameras):
            project_point = camera.project(p)

            if project_point:
                u = project_point.x  # u pixel coordinates in camera
                v = project_point.y  # v pixel coordinates in camera

                if 0 <= u <= camera.sensor.width and 0 <= v <= camera.sensor.height:
                    # Extract video and frame_seq from the camera label
                    camera_label_parts = camera.label.split('_')
                    video = '_'.join(camera_label_parts[:-1])
                    frame_seq = camera_label_parts[-1]

                    data_list.append([point_idx + 1, camera.label, video, frame_seq, u, v])

    columns = ['Point', 'Camera', 'video', 'frame_seq', 'u', 'v']
    df = pd.DataFrame(data_list, columns=columns)
    return df

# Define global coordinates for multiple points
points = list_coordinates('/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/Solitude/output/points_xyz.txt')

# Use active Metashape document
doc = Metashape.app.document

# Iterate through all chunks in the document
df = pd.DataFrame()
for chunk in doc.chunks:
    if chunk.label != 'BaseMap':
        # Set the current chunk to the one being processed
        doc.chunk = chunk

        # Process the current chunk
        tmp = process_chunk(chunk, points)
        df = pd.concat([df, tmp], ignore_index=True)

# Save the results to a CSV file
df.to_csv('/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/Solitude/output/points_uv.csv', index=False)
