VERSION = 0.3.0
NAME = yoga-spin

BASE_DIR = build
INSTALL_PATH=$(BASE_DIR)/$(NAME)_$(VERSION)_all

DEBIAN_DIR = $(INSTALL_PATH)/DEBIAN
DEBIAN_CONTROL = control
DEBIAN_SCRIPTS = \
postinst \
postrm

BIN_DIR = $(INSTALL_PATH)/usr/bin
BIN = spin.py

ICONS_DIR = $(INSTALL_PATH)/usr/share/icons/hicolor/scalable/apps
ICONS = \
yoga-spin-lock.svg \
yoga-spin-touch.svg \
yoga-spin-mode.svg

APPS_DIR = $(INSTALL_PATH)/usr/share/applications
APPS = \
yoga-spin-lock.desktop \
yoga-spin-touch.desktop \
yoga-spin-mode.desktop

all:

install:
	install -d $(INSTALL_PATH)
	install -d $(DEBIAN_DIR)
	install -m 644 $(addprefix package/DEBIAN/,$(DEBIAN_CONTROL)) $(DEBIAN_DIR)
	install -m 755 $(addprefix package/DEBIAN/,$(DEBIAN_SCRIPTS)) $(DEBIAN_DIR)
	install -d $(ICONS_DIR)
	install -m 644 $(addprefix package/icons/,$(ICONS)) $(ICONS_DIR)
	install -d $(APPS_DIR)
	install -m 644 $(addprefix package/applications/,$(APPS)) $(APPS_DIR)
	install -d $(BIN_DIR)
	install -m 755 $(BIN) $(BIN_DIR)
	dpkg-deb -b $(INSTALL_PATH)

clean:
	rm -rf $(INSTALL_PATH)
	rm  $(INSTALL_PATH).deb
