bl_info = {
    "name": "Distool: Displacement & Normal Generator",
    "author": "wsmnb12-Alan+AI",
    "version": (2, 1, 0),
    "blender": (4, 5, 0),
    "location": "Shader Editor > Sidebar > Distool",
    "description": "Advanced normal/displacement map generator with multiple gradient operators and detail enhancement",
    "category": "Node",
    "warning": "",
    "wiki_url": "",
    "tracker_url": ""
}

import sys
import os
import urllib.request
import zipfile


addon_dir = os.path.dirname(__file__)
lib_dir = os.path.join(addon_dir, "libs")

# Ensure lib path is added to Python path
if lib_dir not in sys.path:
    sys.path.append(lib_dir)


def download_and_extract_lib():
    if os.path.exists(lib_dir):
        return  # already exists

    zip_url = "https://github.com/wsmnb12/Distool-/releases/download/libs/libs.zip" 
    tmp_zip = os.path.join(addon_dir, "libs.zip")

    try:
        print(f"[Distool] Downloading dependencies from {zip_url} ...")
        urllib.request.urlretrieve(zip_url, tmp_zip)
        with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
            zip_ref.extractall(addon_dir)
        os.remove(tmp_zip)
        print("[Distool] Dependencies installed successfully.")
    except Exception as e:
        print(f"[Distool] Failed to download/extract libs.zip: {e}")


download_and_extract_lib()


try:
    import numpy
    import scipy
    import cv2
except ImportError as e:
    print(f"[Distool] Error importing dependencies after install: {e}")


from . import distool_main

def register():
    distool_main.register()

def unregister():
    distool_main.unregister()
