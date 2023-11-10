import os
import shutil

src_dir = r'C:\Users\Lenovo\Desktop\dataset'

dest_dir = 'testing'

for foldername in os.listdir(src_dir):
    folderpath = os.path.join(src_dir, foldername)
    if os.path.isdir(folderpath):
        for filename in os.listdir(folderpath):
            if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('jpeg'):
                filepath = os.path.join(folderpath, filename)
                shutil.copy(filepath, dest_dir)