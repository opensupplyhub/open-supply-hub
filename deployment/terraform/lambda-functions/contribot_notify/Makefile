CONTRIBOT_SRC = ../../../../src/contribot
STAGING = .staging
ZIP = contribot_notify.zip

all:
	rm -f $(ZIP)
	rm -rf $(STAGING)
	mkdir -p $(STAGING)/lib
	cp $(CONTRIBOT_SRC)/notify/handler.py $(STAGING)/
	cp $(CONTRIBOT_SRC)/notify/message.py $(STAGING)/
	cp $(CONTRIBOT_SRC)/lib/__init__.py $(STAGING)/lib/
	cp $(CONTRIBOT_SRC)/lib/lists_repository.py $(STAGING)/lib/
	cp $(CONTRIBOT_SRC)/lib/slack_webhook.py $(STAGING)/lib/
	(cd $(STAGING) && zip -qXr ../$(ZIP) .)
	rm -rf $(STAGING)

.PHONY: all
