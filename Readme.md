# State

| Binding | Windows | Linux |
|---------|:-------:|:-----:|
| PyQt5   |    ✅    |   ✅   |
| PyQt6   |    ❌    |   ❌   |
| PySide2 |    ✅    |   ✅   |
| PySide6 |    ✅    |   ✅   |

# Installation

1. **Install these tools**

   - [Compatible Python version](https://www.python.org/downloads)
   - [uv](https://github.com/astral-sh/uv)
   - [just](https://github.com/casey/just)
   - **Windows users also need**
     - [Git Bash](https://git-scm.com/downloads)
     - Be sure to run `just` inside Git Bash

1. **Clone the repository**

1. **Open a terminal** where you cloned it

1. **Initialize the environment**

   ```console
   just init
   ```

1. **Add libmpv to your path**

   - **Linux**: Install `libmpv` through your package manager
   - **Windows**: Download [libmpv (mpv-dev-x86_64)](https://github.com/shinchiro/mpv-winbuild-cmake/releases), extract
     it, and place the `libmpv-*.dll` in the repository’s root folder

1. **Run the sample**

   ```console
   just run-<pyside2|pyside6|pyqt5|pyqt6>
   ```

# Video Licences

Videos are from: https://github.com/Matroska-Org/matroska-test-files

Both Big Buck Bunny and Elephant Dreams and licensed under the Creative Common License Attribution license, also known
as CC-BY.

The recommended license text for Big Buck Bunny is (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org.

The recommended license text for Elephant Dreams is (c) copyright 2006, Blender Foundation / Netherlands Media Art
Institute / www.elephantsdream.org.
