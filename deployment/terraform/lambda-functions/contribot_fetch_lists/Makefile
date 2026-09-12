CONTRIBOT_SRC = ../../../../src/contribot
STAGING = .staging
ZIP = contribot_fetch_lists.zip

all:
	rm -f $(ZIP)
	rm -rf $(STAGING)
	mkdir -p $(STAGING)/lib
	cp $(CONTRIBOT_SRC)/fetch_lists/handler.py $(STAGING)/
	cp $(CONTRIBOT_SRC)/lib/__init__.py $(STAGING)/lib/
	cp $(CONTRIBOT_SRC)/lib/lists_repository.py $(STAGING)/lib/
	cp $(CONTRIBOT_SRC)/lib/os_hub_api.py $(STAGING)/lib/
	(cd $(STAGING) && zip -qXr ../$(ZIP) .)
	rm -rf $(STAGING)

.PHONY: all
