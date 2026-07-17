CONTRIBOT_SRC = ../../../../src/contribot

all:
	rm -f contribot_notify.zip
	(cd $(CONTRIBOT_SRC)/notify && zip -qXr ../../../deployment/terraform/lambda-functions/contribot_notify/contribot_notify.zip handler.py)

.PHONY: all
