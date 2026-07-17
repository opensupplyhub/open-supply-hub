CONTRIBOT_SRC = ../../../../src/contribot
# Fixed mtime so plan/apply CI jobs produce identical zip hashes.
ZIP_MTIME = 198001010000.00

all:
	rm -rf .build contribot_notify.zip
	mkdir -p .build
	cp $(CONTRIBOT_SRC)/notify/handler.py .build/handler.py
	touch -t $(ZIP_MTIME) .build/handler.py
	(cd .build && zip -qXr ../contribot_notify.zip handler.py)
	rm -rf .build

.PHONY: all
