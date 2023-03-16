# Installation

1. Clone this repository
1. Setup virtual environment:
    1. `python -m venv venv`
    1. `source venv/bin/activate` (*bash*) or `source venv/bin/activate.fish` (*fish*)
1. Install requirements `python -m pip install -r requirements.txt`
1. Make sure you have
   1. Windows: 
      1. mpv-2.dll in the root of this repository (will start the download immediately https://sourceforge.net/projects/mpv-player-windows/files/libmpv/mpv-dev-x86_64-20230101-git-ad65c88.7z)
   2. Linux: 
      1. libmpv installed (libmpv1 package on Ubuntu)

# Testing

1. Run `python3 pyside6-workaround.py`. 
   1. The window should be black and contain some QML controls. 
      Clicking into the window should start a video.
1. Apply the patch that potentially fixes pyside-971
1. Run `python3 pyside6-patched.py`
   1. It should lead to the same result as the workaround

## Video Licences

Videos are from: https://github.com/Matroska-Org/matroska-test-files

Both Big Buck Bunny and Elephant Dreams and licensed under the Creative Common License Attribution license, also known
as CC-BY.

The recommended license text for Big Buck Bunny is (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org.

The recommended license text for Elephant Dreams is (c) copyright 2006, Blender Foundation / Netherlands Media Art
Institute / www.elephantsdream.org.
