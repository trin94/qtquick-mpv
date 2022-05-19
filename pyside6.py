import ctypes
import os
import platform

from PySide6 import QtWidgets
from PySide6.QtCore import QSize, QUrl, Slot, Signal
from PySide6.QtOpenGL import QOpenGLFramebufferObject
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickFramebufferObject, QQuickView, QSGRendererInterface, QQuickWindow

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
from mpv import MPV, MpvGlGetProcAddressFn, MpvRenderContext

system = platform.system()


def get_process_address(_, name_bytes: bytes):
    name_str: str = name_bytes.decode("utf-8")

    if system == 'Linux':
        from OpenGL import GLX
        address = GLX.glXGetProcAddress(name_str)
    elif system == 'Windows':
        from OpenGL import WGL
        address = WGL.wglGetProcAddress(name_bytes)
    else:
        raise NotImplementedError(f'System {system} not implemented')

    address = ctypes.cast(address, ctypes.c_void_p).value

    # print("func", name_str, 'address', address)

    return address


class MpvObject(QQuickFramebufferObject):
    """QML widget"""

    onUpdate = Signal()

    def __init__(self, parent=None):
        print("MpvObject.init")
        super(MpvObject, self).__init__(parent)
        self.mpv = MPV(ytdl=True, vo='libmpv', terminal="yes", msg_level="all=v")
        self.mpv_gl = None
        self._proc_addr_wrapper = MpvGlGetProcAddressFn(get_process_address)
        self.onUpdate.connect(self.doUpdate)

    def on_update(self):
        self.onUpdate.emit()

    @Slot()
    def doUpdate(self):
        self.update()

    def createRenderer(self) -> 'QQuickFramebufferObject.Renderer':
        return MpvRenderer(self)

    @Slot(str)
    def play(self, url):
        print("MpvObject.play")
        self.mpv.play(url)


class MpvRenderer(QQuickFramebufferObject.Renderer):
    """MpvRenderer:
    This class implements the QQuickFramebufferObject's Renderer subsystem.
    It augments the base renderer with an instance of mpv's render API."""

    def __init__(self, parent: QQuickFramebufferObject):
        print("MpvRenderer.init")
        super(MpvRenderer, self).__init__()
        self.obj = parent
        self.ctx = None

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        print("MpvRenderer.createFramebufferObject")

        if self.ctx is None:
            self.ctx = MpvRenderContext(self.obj.mpv, 'opengl',
                                        opengl_init_params={'get_proc_address': self.obj._proc_addr_wrapper})
            self.ctx.update_cb = self.obj.on_update

        return QQuickFramebufferObject.Renderer.createFramebufferObject(self, size)

    def render(self):
        if self.ctx:
            factor = self.obj.scale()
            rect = self.obj.size()

            # width and height are floats
            width = int(rect.width() * factor)
            height = int(rect.height() * factor)
            fbo = int(self.framebufferObject().handle())

            self.ctx.render(flip_y=False, opengl_fbo={'w': width, 'h': height, 'fbo': fbo})


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGL)

    qmlRegisterType(MpvObject, 'mpvtest', 1, 0, "MpvObject")

    view = QQuickView()

    url = QUrl("window.qml")

    import locale

    locale.setlocale(locale.LC_NUMERIC, 'C')

    view.setSource(url)
    view.show()
    app.exec()
