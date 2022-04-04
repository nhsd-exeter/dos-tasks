PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

build: project-config # Build project - mandatory: TASK=[hk task]
	make docker-build NAME=hk-filter
		if [ $(TASK) == 'all' ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make docker-build NAME="hk-$$task"
		done
	else
		make docker-build NAME=hk-$(TASK)
	fi

start: project-start # Start project

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

test: # Test project
	make start
	make stop

push: # Push project artefacts to the registry - mandatory: TASK=[hk task]
	make docker-push NAME=hk-filter
	if [ $(TASK) == 'all' ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make docker-push NAME="hk-$$task"
		done
	else
		make docker-push NAME=hk-$(TASK)
	fi

provision: # Provision environment - mandatory: PROFILE=[name], TASK=[hk task]
	make terraform-apply-auto-approve STACK=$(STACKS) PROFILE=$(PROFILE)
	if [ $(TASK) == 'all' ]; then
		make terraform-apply-auto-approve STACK=$(TASKS) PROFILE=$(PROFILE)
	else
		make terraform-apply-auto-approve STACK=$(TASK) PROFILE=$(PROFILE)
	fi

unit-test: # Runs unit tests for task - mandatory: TASK=[hk task]
	if [ $(TASK) == 'all' ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make unit-test-task TASK="$$task"
		done
	else
		make unit-test-task TASK=$(TASK)
	fi

clean: # Clean up project

# ==============================================================================
# Supporting targets

trust-certificate: ssl-trust-certificate-project ## Trust the SSL development certificate


pipeline-finalise: ## Finalise pipeline execution - mandatory: PIPELINE_NAME,BUILD_STATUS
	# Check if BUILD_STATUS is SUCCESS or FAILURE
	make pipeline-send-notification

pipeline-send-notification: ## Send Slack notification with the pipeline status - mandatory: PIPELINE_NAME,BUILD_STATUS
	eval "$$(make aws-assume-role-export-variables)"
	eval "$$(make secret-fetch-and-export-variables NAME=$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)-$(PROFILE)/deployment)"
	make slack-it

# ==============================================================================

.SILENT:
