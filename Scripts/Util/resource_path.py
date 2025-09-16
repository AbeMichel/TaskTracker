import os
import sys

def resourcePath(relativePath):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
        base_path = os.path.join(base_path, "../../")
    return os.path.join(base_path, relativePath)