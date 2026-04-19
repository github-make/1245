.PHONY: all build build-linux build-macos build-windows clean install-deps

PYINSTALLER := pyinstaller
PYTHON := python3

all: build

install-deps:
	$(PYTHON) -m pip install pyinstaller

build: install-deps
	$(PYTHON) build.py build

build-linux: install-deps
	$(PYTHON) build.py build linux

build-macos: install-deps
	$(PYTHON) build.py build macos

build-windows: install-deps
	$(PYTHON) build.py build windows

build-all: install-deps
	$(PYTHON) build.py all

clean:
	$(PYTHON) build.py clean

dist-linux: build-linux
	@echo "输出目录: dist/linux/"

dist-macos: build-macos
	@echo "输出目录: dist/macos/"

dist-windows: build-windows
	@echo "输出目录: dist/windows/"
