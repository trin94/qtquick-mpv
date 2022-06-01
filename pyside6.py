import ctypes
import platform

from PySide6 import QtWidgets
from PySide6.QtCore import QSize, QUrl, Slot, Signal
from PySide6.QtOpenGL import QOpenGLFramebufferObject
from PySide6.QtQml import qmlRegisterType
from PySide6.QtQuick import QQuickFramebufferObject, QQuickView, QSGRendererInterface, QQuickWindow

if platform.system() == 'Windows':
    import os

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

    def __init__(self, parent):
        super(MpvRenderer, self).__init__()
        self._parent = parent
        self._get_proc_address_resolver = MpvGlGetProcAddressFn(GetProcAddressGetter().wrap)
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


class GetProcAddressGetter:
    """ fixme: Class gets obsolete once https://bugreports.qt.io/browse/PYSIDE-971 gets fixed """

    def __init__(self):
        self._func = self._find_platform_wrapper()

    def _find_platform_wrapper(self):
        operating_system = platform.system()
        if operating_system == 'Linux':
            return self._init_linux()
        elif operating_system == 'Windows':
            return self._init_windows()
        raise f'Platform {operating_system} not supported yet'

    def _init_linux(self):
        try:
            from OpenGL import GLX
            return self._glx_impl
        except AttributeError:
            pass
        try:
            from OpenGL import EGL
            return self._egl_impl
        except AttributeError:
            pass
        raise 'Cannot initialize OpenGL'

    def _init_windows(self):
        from PySide6.QtGui import QOpenGLContext
        import glfw

        from PySide6.QtGui import QOffscreenSurface
        self.surface = QOffscreenSurface()
        self.surface.create()

        if not glfw.init():
            raise 'Cannot initialize OpenGL'

        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        window = glfw.create_window(1, 1, "mpvQC-OpenGL", None, None)

        glfw.make_context_current(window)
        QOpenGLContext.currentContext().makeCurrent(self.surface)
        return self._windows_impl

    def wrap(self, _, name: bytes):
        address = self._func(name)
        return ctypes.cast(address, ctypes.c_void_p).value

    @staticmethod
    def _glx_impl(name: bytes):
        from OpenGL import GLX
        return GLX.glXGetProcAddress(name.decode("utf-8"))

    @staticmethod
    def _egl_impl(name: bytes):
        from OpenGL import EGL
        return EGL.eglGetProcAddress(name.decode("utf-8"))

    @staticmethod
    def _windows_impl(name: bytes):
        import glfw
        return glfw.get_proc_address(name.decode('utf8'))


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
