"""
This was built from these three examples.
- https://gist.github.com/jaseg/657e8ecca3267c0d82ec85d40f423caa
- https://gist.github.com/cosven/b313de2acce1b7e15afda263779c0afc
- https://github.com/mpv-player/mpv-examples/tree/master/libmpv/qml
"""

import ctypes

import PyQt6.QtWidgets as QtWidgets
# HELP: currently, we need import GL module，otherwise it will raise seg fault on Linux(Ubuntu 18.04)
# My guess here is that the GL module, when imported, does some sort of necessary
# init that prevents the seg falt
from OpenGL import GL, GLX
from PyQt6.QtCore import QUrl, QSize, pyqtSignal, pyqtSlot
from PyQt6.QtOpenGL import QOpenGLFramebufferObject
from PyQt6.QtQml import qmlRegisterType
from PyQt6.QtQuick import QQuickFramebufferObject, QQuickView
from mpv import MPV, MpvRenderContext, OpenGlCbGetProcAddrFn


def get_process_address(_, name):
    """This function allows looking up OpenGL functions."""
    address = GLX.glXGetProcAddress(name.decode("utf-8"))
    return ctypes.cast(address, ctypes.c_void_p).value


class MpvObject(QQuickFramebufferObject):
    """MpvObject:
    This is a QML widget that can be used to embed the output of a mpv instance.
    It extends the QQuickFramebufferObject class to implement this functionality."""

    # This signal allows triggers the update function to run on the correct thread
    onUpdate = pyqtSignal()

    def __init__(self, parent=None):
        print("Creating MpvObject")
        super(MpvObject, self).__init__(parent)
        self.mpv = MPV(ytdl=True)
        self.mpv_gl = None
        self._proc_addr_wrapper = OpenGlCbGetProcAddrFn(get_process_address)
        # self.onUpdate.connect(self.doUpdate)

    def on_update(self):
        """Function for mpv to call to trigger a framebuffer update"""
        print("on update")
        self.onUpdate.emit()

    @pyqtSlot()
    def doUpdate(self):
        """Slot for receiving the update event on the correct thread"""
        print("doUpdate")
        self.update()

    def createRenderer(self) -> 'QQuickFramebufferObject.Renderer':
        """Overrides the default createRenderer function to create a
        MpvRenderer instance"""
        print("Calling overridden createRenderer")
        return MpvRenderer(self)

    @pyqtSlot(str)
    def play(self, url):
        print("play", url)
        """Temporary adapter fuction that allowing playing media from QML"""
        self.mpv.play(url)


class MpvRenderer(QQuickFramebufferObject.Renderer):
    """MpvRenderer:
    This class implements the QQuickFramebufferObject's Renderer subsystem.
    It augments the base renderer with an instance of mpv's render API."""

    def __init__(self, parent=None):
        print("Creating MpvRenderer")
        super(MpvRenderer, self).__init__()
        self.obj = parent
        self.ctx = None

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        """Overrides the base createFramebufferObject function, augmenting it to
        create an MpvRenderContext using opengl"""
        if self.obj.mpv_gl is None:
            print("Creating mpv gl")
            self.ctx = MpvRenderContext(self.obj.mpv, 'opengl',
                                        opengl_init_params={
                                            'get_proc_address': self.obj._proc_addr_wrapper
                                        })
            # self.ctx.update_cb = self.obj.on_update

        print("return")
        return QQuickFramebufferObject.Renderer.createFramebufferObject(self, size)

    def render(self):
        """Overrides the base render function, calling mpv's render functions instead"""
        print("render")
        if self.ctx:
            factor = self.obj.scale()
            rect = self.obj.size()

            # width and height are floats
            width = int(rect.width() * factor)
            height = int(rect.height() * factor)

            fbo = GL.glGetIntegerv(GL.GL_DRAW_FRAMEBUFFER_BINDING)
            self.ctx.render(flip_y=False, opengl_fbo={'w': width, 'h': height, 'fbo': fbo})

    def synchronize(self, a0: 'QQuickFramebufferObject') -> None:
        print("sync")
        return super(MpvRenderer, self).synchronize(a0)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    # QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGLRhi)

    qmlRegisterType(MpvObject, 'mpvtest', 1, 0, "MpvObject")

    view = QQuickView()

    url = QUrl("layouts/mpv.qml")

    import locale

    locale.setlocale(locale.LC_NUMERIC, 'C')

    view.setSource(url)
    view.show()
    app.exec()
