Installation
============

1. ```python -m venv venv```
2. ```source venv/bin/activate``` (bash) or ``source venv/bin/activate.fish``` (fish)
3. Install requirements ```python -m pip install -r requirements.txt```



This is an example of embedding MPV into QML using python-mpv and PyQt5.

Make sure to install all the needed dependencies (listed in the pyproject.toml file).
Also make sure to clone the submodules to grab the Video files that are being used.

This example isn't 100% (it still segfaults sometimes). Feel free to submit a PR
if you have any additions or corrections. Thanks and enjoy!


Code References
===============
This was built from these three examples.
    - https://gist.github.com/jaseg/657e8ecca3267c0d82ec85d40f423caa
    - https://gist.github.com/cosven/b313de2acce1b7e15afda263779c0afc
    - https://github.com/mpv-player/mpv-examples/tree/master/libmpv/qml


Video Licences
==============

Videos are from: https://github.com/Matroska-Org/matroska-test-files

Both Big Buck Bunny and Elephant Dreams and licensed under the Creative Common License Attribution license, also known as CC-BY.

The recommended license text for Big Buck Bunny is (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org.

The recommended license text for Elephant Dreams is (c) copyright 2006, Blender Foundation / Netherlands Media Art Institute / www.elephantsdream.org.

