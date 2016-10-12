include config.mk

all:
	@echo 'Nothing to build'

install:
	SKIP_ICON_CACHE_UPDATE=1 ./install.sh --prefix='$(PREFIX)' $(if $(DESTDIR),--destdir='$(DESTDIR)')

.PHONY: install
