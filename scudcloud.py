#!/usr/bin/env python3
INSTALL_DIR = "/opt/scudcloud/"
import sys, os, json, subprocess
sys.path.append(INSTALL_DIR+'lib')
import notify2
from cookiejar import PersistentCookieJar
from gi.repository import Unity, GObject, Dbusmenu
from os.path import expanduser
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
from PyQt4.QtCore import QUrl, QSettings
from PyQt4.QtWebKit import QWebSettings

class ScudCloud(QtGui.QMainWindow):

    APP_NAME = "ScudCloud Client"
    SIGNIN_URL = "https://slack.com/signin"

    def __init__(self, parent=None):
        super(ScudCloud, self).__init__(parent)
        self.setWindowTitle('ScudCloud')
        notify2.init(self.APP_NAME)
        self.newMessages = 0
        self.settings = QSettings(expanduser("~")+"/.scudcloud", QSettings.IniFormat)
        self.identifier = self.settings.value("Domain")
        with open (INSTALL_DIR+"resources/notifications.js", "r") as f:
             self.js=f.read()
        self.launcher = Unity.LauncherEntry.get_for_desktop_id("scudcloud.desktop")
        self.resize(800, 600)
        self.centralwidget = QtGui.QWidget(self)
        self.mainLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(0)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.gridLayout = QtGui.QVBoxLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.webView = QtWebKit.QWebView()
        self.webView.urlChanged.connect(self.urlChanged)
        self.webView.titleChanged.connect(self.titleChanged)
        self.webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.webView.linkClicked.connect(self.linkClicked)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True)
        QWebSettings.globalSettings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        self.gridLayout.addWidget(self.webView)
        self.mainLayout.addWidget(self.frame)
        self.setCentralWidget(self.centralwidget)
        self.cookiesjar = PersistentCookieJar(self)
        self.webView.page().networkAccessManager().setCookieJar(self.cookiesjar)
        self.webView.load(QtCore.QUrl(self.domain()))
        self.webView.show()

    def focusInEvent(self, event):
        self.launcher.set_property("urgent", False)

    def titleChanged(self):
        self.setWindowTitle(self.webView.title())

    def domain(self):
        if self.identifier is None:
            return self.SIGNIN_URL
        else:
            if self.identifier.endswith(".slack.com"):
                return self.identifier
            else:
                return "https://"+self.identifier+".slack.com"

    def closeEvent(self, event):
        self.cookiesjar.save()

    @QtCore.pyqtSlot(str, str) 
    def sendMessage(self, title, message):
        notice = notify2.Notification(str(title).replace("New message from ", ""), str(message), INSTALL_DIR+"resources/scudcloud.png")
        notice.show()

    def urlChanged(self):
        if self.SIGNIN_URL != self.webView.url().toString():
            self.settings.setValue("Domain", 'https://'+self.webView.url().host())
        if self.domain() == self.webView.url().toString():
            self.webView.settings().setUserStyleSheetUrl(QUrl.fromLocalFile(INSTALL_DIR+"/resources/login.css"))
        else:
            self.webView.page().currentFrame().addToJavaScriptWindowObject("desktop", self)
            self.quicklist(self.webView.page().currentFrame().evaluateJavaScript(self.js))

    def quicklist(self, channels):
        if channels is None:
            self.launcher.set_property("quicklist", None)
        else:
            ql = Dbusmenu.Menuitem.new ()
            for c in channels:
                if c['is_member']:
                    item = Dbusmenu.Menuitem.new ()
                    item.property_set (Dbusmenu.MENUITEM_PROP_LABEL, "#"+c['name'])
                    item.property_set ("id", c['name'])
                    item.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, True)
                    item.connect(Dbusmenu.MENUITEM_SIGNAL_ITEM_ACTIVATED, self.openChannel)
                    ql.child_append (item)
            self.launcher.set_property("quicklist", ql)

    def openChannel(self, menuitem, timestamp):
        self.webView.page().currentFrame().evaluateJavaScript("join('"+menuitem.property_get("id")+"');")
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()

    def linkClicked(self, url):
        subprocess.call(('xdg-open', url.toString()))

    @QtCore.pyqtSlot(int) 
    def count(self, value):
        if value > self.newMessages:
            if not self.isActiveWindow():
                self.launcher.set_property("urgent", True)
        elif 0 == value:
            self.launcher.set_property("urgent", False)
            self.launcher.set_property("count_visible", False)
        else:
            self.launcher.set_property("count", value)
            self.launcher.set_property("count_visible", True)
        self.newMessages = value
