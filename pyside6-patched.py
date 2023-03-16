import platform

from PySide6 import QtWidgets
from PySide6.QtCore import QSize, QUrl, Slot, Signal
from PySide6.QtGui import QOpenGLContext
from PySide6.QtOpenGL import QOpenGLFramebufferObject
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickFramebufferObject, QQuickView, QSGRendererInterface, QQuickWindow

if platform.system() == 'Windows':
    import os

    os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]

from mpv import MPV, MpvGlGetProcAddressFn, MpvRenderContext


def get_process_address(_, name):
    print("get_process_address", name.decode('utf-8'))
    glctx = QOpenGLContext.currentContext()
    if glctx is None:
        return 0
    return int(glctx.getProcAddress(name))


class MpvObject(QQuickFramebufferObject):
    onUpdate = Signal()

    def __init__(self, parent=None):
        print("MpvObject.init")
        super(MpvObject, self).__init__(parent)
        self.mpv = MPV(ytdl=True, vo='libmpv', terminal="yes", msg_level="all=v")
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

    def __init__(self, parent):
        super(MpvRenderer, self).__init__()
        self._parent = parent
        self._get_proc_address_resolver = MpvGlGetProcAddressFn(get_process_address)
        self._ctx = None

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        if self._ctx is None:
            self._ctx = MpvRenderContext(
                self._parent.mpv,
                api_type='opengl',
                opengl_init_params={'get_proc_address': self._get_proc_address_resolver}
            )
            self._ctx.update_cb = self._parent.onUpdate.emit

        return QQuickFramebufferObject.Renderer.createFramebufferObject(self, size)

    def render(self):
        if self._ctx:
            factor = self._parent.scale()
            rect = self._parent.size()

            width = int(rect.width() * factor)
            height = int(rect.height() * factor)
            fbo = int(self.framebufferObject().handle())

            self._ctx.render(flip_y=False, opengl_fbo={'w': width, 'h': height, 'fbo': fbo})


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
