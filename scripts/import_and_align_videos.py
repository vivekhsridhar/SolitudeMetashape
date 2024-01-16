import Metashape
import datetime
import glob
import os
import pathlib
import numpy as np
import helper_functions as hf

doc = Metashape.app.document
reference_chunk = doc.chunk.key

# The directory where videos are saved
VideoDirectory = "/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/Solitude/images/"

# The directory where frames must be imported
ImportDirectory = "/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/Solitude/images/"

def list_videos(directory):
    directory_path = pathlib.Path(directory)
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
    video_files = [(str(file.resolve()), file.stem) for file in directory_path.iterdir() if file.suffix.lower() in video_extensions]
    return video_files
def import_frames(video_path, video_name, import_directory):
    # Create a folder for each video
    video_folder = os.path.join(import_directory, video_name)
    os.makedirs(video_folder, exist_ok=True)

    # Add a new chunk for each video
    chunk = doc.addChunk()
    chunk.label = video_name
    doc.chunks.append(chunk)

    # Define the image names pattern for frames
    image_names = os.path.join(video_folder, f'{video_name}_{{filenum:04}}.png')

    # Import frames with custom frame step
    chunk.importVideo(video_path, image_names, frame_step=Metashape.FrameStep.CustomFrameStep, custom_frame_step=20)


hf.log( "--- Starting workflow ---" )
hf.log( "Metashape version " + Metashape.Application().version )
hf.log_time()

# List videos in VideoDirectory
videos = list_videos(VideoDirectory)

# Import frames from listed videos
for video_path, video_name in videos:
    import_frames(video_path, video_name, ImportDirectory)


# Parameters for feature matching photos
match_photos_config = {
    'downscale': 1,
    'generic_preselection': True,
    'reference_preselection': True,
    'reference_preselection_mode': Metashape.ReferencePreselectionEstimated
}

chunk_dirs = hf.get_subdirectories(ImportDirectory, ignore_files=['.DS_Store'])

all_chunks = [reference_chunk]
# Match photos and align cameras
for chunk in doc.chunks:
    if chunk.label != 'BaseMap':
        hf.log( "Processing chunk" )

        chunk.matchPhotos(**match_photos_config)
        chunk.alignCameras()
        all_chunks.append(chunk.key)

doc.alignChunks(chunks=all_chunks, reference=reference_chunk)

hf.log_time()
hf.log( "--- Finished workflow ---")

doc.save('/Users/vivekhsridhar/Library/Mobile Documents/com~apple~CloudDocs/Documents/Metashape/Solitude/Solitude.psx')
