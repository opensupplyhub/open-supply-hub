CONTRIBOT_SRC = ../../../../src/contribot

all:
	rm -f contribot_fetch_lists.zip
	(cd $(CONTRIBOT_SRC)/fetch_lists && zip -qXr ../../../deployment/terraform/lambda-functions/contribot_fetch_lists/contribot_fetch_lists.zip handler.py)

.PHONY: all
