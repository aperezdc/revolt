
APP_ID ?= org.perezdecastro.Revolt

all: $(APP_ID).gresource

config.mk: configure
	@echo '==== Running "configure" script...'
	@./configure
	@echo '==== Run "configure --help" for more options'

-include config.mk

RESOURCE_FILES := $(wildcard gtk/*.ui gtk/*.css icon/*.svg)
$(APP_ID).gresource: $(APP_ID).gresources.xml $(RESOURCE_FILES)
	glib-compile-resources --target=$@ $<

gschemas.compiled: $(APP_ID).gschema.xml
	glib-compile-schemas .

run: $(APP_ID).gresource gschemas.compiled
	XDG_DATA_DIRS="$${XDG_DATA_DIRS}:$(CURDIR)" GSETTINGS_SCHEMA_DIR='$(CURDIR)' __REVOLT_DEVELOPMENT=1 '$(CURDIR)/bin/revolt'

install:
	SKIP_ICON_CACHE_UPDATE=1 ./install.sh --prefix='$(PREFIX)' $(if $(DESTDIR),--destdir='$(DESTDIR)')
	python3 -m compileall $(if $(DESTDIR),-d '$(DESTDIR)') $(DESTDIR)$(PREFIX)/share/revolt/py/revolt/*.py

.PHONY: install run
