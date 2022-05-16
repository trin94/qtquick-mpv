import ctypes

# HELP: currently, we need import GL module，otherwise it will raise seg fault on Linux(Ubuntu 18.04)
# My guess here is that the GL module, when imported, does some sort of necessary
# init that prevents the seg falt
from OpenGL import GLX
from PySide2 import QtWidgets
from PySide2.QtCore import QSize, QUrl, Slot, Signal
from PySide2.QtGui import QOpenGLFramebufferObject
from PySide2.QtQml import qmlRegisterType
from PySide2.QtQuick import QQuickFramebufferObject, QQuickView
from mpv import MPV, MpvRenderContext, MpvGlGetProcAddressFn


def get_process_address(_, name):
    print("get_process_address", name.decode('utf-8'))
    address = GLX.glXGetProcAddress(name.decode("utf-8"))
    return ctypes.cast(address, ctypes.c_void_p).value


class MpvObject(QQuickFramebufferObject):
    """QML widget"""

    onUpdate = Signal()

    def __init__(self, parent=None):
        print("MpvObject.init")
        super(MpvObject, self).__init__(parent)
        self.mpv = MPV(ytdl=True)  # terminal="yes", msg_level="all=v", vo="gpu")
        self.mpv_gl = None
        self._proc_addr_wrapper = MpvGlGetProcAddressFn(get_process_address)
        self.onUpdate.connect(self.doUpdate)

    def on_update(self):
        print("MpvObject.on_update")
        self.onUpdate.emit()

    @Slot()
    def doUpdate(self):
        print("MpvObject.doUpdate")
        self.update()

    def createRenderer(self) -> 'QQuickFramebufferObject.Renderer':
        print("MpvObject.createRenderer")
        # todo: Workaround https://bugreports.qt.io/browse/PYSIDE-1868
        # Once the fix is rolled out, this should be inlined
        self._x = MpvRenderer(self)
        return self._x

    @Slot(str)
    def play(self, url):
        print("MpvObject.play")
        self.mpv.play(url)


class MpvRenderer(QQuickFramebufferObject.Renderer):
    """MpvRenderer:
    This class implements the QQuickFramebufferObject's Renderer subsystem.
    It augments the base renderer with an instance of mpv's render API."""

    def __init__(self, parent=None):
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
        print("MpvRenderer.render")

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

    qmlRegisterType(MpvObject, 'mpvtest', 1, 0, "MpvObject")

    view = QQuickView()

    url = QUrl("window.qml")

    import locale

    locale.setlocale(locale.LC_NUMERIC, 'C')

    view.setSource(url)
    view.show()
    app.exec_()
