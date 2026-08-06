CONTRIBOT_SRC = ../../../../src/contribot

all:
	rm -f contribot_process_list.zip
	(cd $(CONTRIBOT_SRC)/process_list && zip -qXr ../../../deployment/terraform/lambda-functions/contribot_process_list/contribot_process_list.zip handler.py)

.PHONY: all
