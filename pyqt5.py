"""
Copyright: https://gitlab.com/robozman/python-mpv-qml-example

This was built from these three examples.
- https://gist.github.com/jaseg/657e8ecca3267c0d82ec85d40f423caa
- https://gist.github.com/cosven/b313de2acce1b7e15afda263779c0afc
- https://github.com/mpv-player/mpv-examples/tree/master/libmpv/qml
"""

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import QUrl, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QOpenGLFramebufferObject, QOpenGLContext
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtQuick import QQuickFramebufferObject, QQuickView
from mpv import MPV, MpvRenderContext, MpvGlGetProcAddressFn


def get_process_address(_, name):
    print("get_process_address", name.decode('utf-8'))
    glctx = QOpenGLContext.currentContext()
    if glctx is None:
        return 0
    return int(glctx.getProcAddress(name))


class MpvObject(QQuickFramebufferObject):
    """QML widget"""

    onUpdate = pyqtSignal()

    def __init__(self, parent=None):
        print("MpvObject.init")
        super(MpvObject, self).__init__(parent)
        self.mpv = MPV(ytdl=True, vo='libmpv', terminal="yes", msg_level="all=v")
        self.mpv_gl = None
        self._proc_addr_wrapper = MpvGlGetProcAddressFn(get_process_address)
        self.onUpdate.connect(self.doUpdate)

    def on_update(self):
        self.onUpdate.emit()

    @pyqtSlot()
    def doUpdate(self):
        self.update()

    def createRenderer(self) -> 'QQuickFramebufferObject.Renderer':
        print("MpvObject.createRenderer")
        return MpvRenderer(self)

    @pyqtSlot(str)
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
