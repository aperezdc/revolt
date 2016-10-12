include config.mk

all:
	@echo 'Nothing to build'

install:
	./install.sh --prefix='$(PREFIX)' $(if $(DESTDIR),--destdir='$(DESTDIR)')

.PHONY: install
