CONTRIBOT_SRC = ../../../../src/contribot
STAGING = .staging
ZIP = contribot_process_list.zip
REQUIREMENTS = $(CONTRIBOT_SRC)/requirements.txt

# Must match aws_lambda_function.contribot_process_list.runtime.
PYTHON_VERSION = 3.10
# Default Lambda arch is x86_64 (no architectures = [...] override in Terraform).
LAMBDA_PLATFORM = manylinux2014_x86_64

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
	# Cross-compile for the Lambda runtime: host pip may be a different Python
	# (e.g. 3.11), which produces cpython-311 .so files that fail to import on
	# python3.10 with Runtime.ImportModuleError for numpy/pandas.
	pip install -q -t $(STAGING) -r $(REQUIREMENTS) \
		--platform $(LAMBDA_PLATFORM) \
		--implementation cp \
		--python-version $(PYTHON_VERSION) \
		--only-binary=:all:
	for pkg in $(EXCLUDE_PACKAGES); do \
		pkg_hyphen=$$(echo "$$pkg" | tr '_' '-'); \
		rm -rf $(STAGING)/$$pkg $(STAGING)/$$pkg-*.dist-info $(STAGING)/$$pkg_hyphen-*.dist-info; \
	done
	# Keep only Drive v3 discovery (full documents/ is ~79MB). build() defaults
	# to static_discovery=True and raises UnknownApiNameOrVersion without it.
	find $(STAGING)/googleapiclient/discovery_cache/documents -type f ! -name 'drive.v3.json' -delete 2>/dev/null || true
	find $(STAGING) -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name 'tests' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name 'test' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name '*.dist-info' -exec rm -rf {} + 2>/dev/null || true
	find $(STAGING) -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	(cd $(STAGING) && zip -qXr ../$(ZIP) .)
	rm -rf $(STAGING)

.PHONY: all
