LAMBDA_FUNCTIONS = contribot_fetch_lists contribot_process_list contribot_notify contribot_retry_failed_lists

all: $(LAMBDA_FUNCTIONS)

$(LAMBDA_FUNCTIONS):
	$(MAKE) -C ../../deployment/terraform/lambda-functions/$@

.PHONY: all $(LAMBDA_FUNCTIONS)
