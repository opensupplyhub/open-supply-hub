CONTRIBOT_SRC = ../../../../src/contribot
STAGING = .staging
ZIP = contribot_process_list.zip
REQUIREMENTS = $(CONTRIBOT_SRC)/requirements.txt

# boto3/botocore ship in the Lambda runtime; bundling them bloats the zip.
EXCLUDE_PACKAGES = boto3 botocore s3transfer jmespath

LIB_MODULES = \
	__init__.py \
	contribot.py \
	known_countries.py \
	utils.py \
	lists_repository.py \
	s3_storage.py \
	google_drive.py \
	0000.error_codes.xlsx

all:
	rm -f $(ZIP)
	rm -rf $(STAGING)
	mkdir -p $(STAGING)/lib
	cp $(CONTRIBOT_SRC)/process_list/handler.py $(STAGING)/
	for f in $(LIB_MODULES); do \
		cp $(CONTRIBOT_SRC)/lib/$$f $(STAGING)/lib/; \
	done
	pip install -q -t $(STAGING) -r $(REQUIREMENTS)
	for pkg in $(EXCLUDE_PACKAGES); do \
		pkg_hyphen=$$(echo "$$pkg" | tr '_' '-'); \
		rm -rf $(STAGING)/$$pkg $(STAGING)/$$pkg-*.dist-info $(STAGING)/$$pkg_hyphen-*.dist-info; \
	done
	rm -rf $(STAGING)/googleapiclient/discovery_cache/documents
	find $(STAGING) -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name 'tests' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name 'test' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name '*.dist-info' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	(cd $(STAGING) && zip -qXr ../$(ZIP) .)
	rm -rf $(STAGING)

.PHONY: all
