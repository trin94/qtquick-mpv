import ctypes
import os
import sys

import glfw
from PySide6 import QtWidgets
from PySide6.QtCore import QSize, QUrl, Slot, Signal
from PySide6.QtGui import QOpenGLContext, QOffscreenSurface
from PySide6.QtOpenGL import QOpenGLFramebufferObject
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickFramebufferObject, QQuickView, QSGRendererInterface, QQuickWindow

os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
from mpv import MPV, MpvGlGetProcAddressFn, MpvRenderContext


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

    def __init__(self, parent: QQuickFramebufferObject):
        print("MpvRenderer.init")
        super(MpvRenderer, self).__init__()
        self.obj = parent
        self.ctx = None
        self.surface = QOffscreenSurface()
        self.surface.create()

    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
        print("MpvRenderer.createFramebufferObject")

        if not self.ctx:
            self._init()

        return QQuickFramebufferObject.Renderer.createFramebufferObject(self, size)

    def _init(self):
        def _init_opengl_context():
            if not glfw.init():
                print('Cannot initialize OpenGL', file=sys.stderr)
                sys.exit(-1)

            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
            window = glfw.create_window(1, 1, "mpvQC-OpenGL", None, None)

            glfw.make_context_current(window)
            QOpenGLContext.currentContext().makeCurrent(self.surface)

        def _get_process_address(_, name):
            address = glfw.get_proc_address(name.decode('utf8'))
            return ctypes.cast(address, ctypes.c_void_p).value

        def _init_render_context():
            wrapper = MpvGlGetProcAddressFn(_get_process_address)
            self.ctx = MpvRenderContext(self.obj.mpv, 'opengl', opengl_init_params={'get_proc_address': wrapper})
            self.ctx.update_cb = self.obj.on_update

        _init_opengl_context()
        _init_render_context()

    def render(self):
        if self.ctx:
            factor = self.obj.scale()
            rect = self.obj.size()

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
