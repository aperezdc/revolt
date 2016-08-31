all:
	@echo 'Nothing to build'

install:
	./install.sh --prefix=/app --destdir=/

.PHONY: install
