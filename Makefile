include config.mk

APP_ID ?= org.perezdecastro.Revolt

all: $(APP_ID).gresource

$(APP_ID).gresource: $(APP_ID).gresources.xml
	glib-compile-resources --target=$@ $<

gschemas.compiled: $(APP_ID).gschema.xml
	glib-compile-schemas .

run: $(APP_ID).gresource gschemas.compiled
	GSETTINGS_SCHEMA_DIR=$(CURDIR) __REVOLT_DEVELOPMENT=1 $(CURDIR)/revolt

install:
	SKIP_ICON_CACHE_UPDATE=1 ./install.sh --prefix='$(PREFIX)' $(if $(DESTDIR),--destdir='$(DESTDIR)')

.PHONY: install run
