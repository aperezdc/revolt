include config.mk

all:
	@echo 'Nothing to build'

gschemas.compiled: $(APP_ID).gschema.xml
	glib-compile-schemas .

run: $(APP_ID).gresource gschemas.compiled
	GSETTINGS_SCHEMA_DIR=$(CURDIR) $(CURDIR)/revolt

install:
	SKIP_ICON_CACHE_UPDATE=1 ./install.sh --prefix='$(PREFIX)' $(if $(DESTDIR),--destdir='$(DESTDIR)')

.PHONY: install run
