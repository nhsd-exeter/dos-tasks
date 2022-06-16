
PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

build: # Build project - mandatory: TASK=[task]
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make build-image NAME=$$task AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		make build-image NAME=$(TASK) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi

build-image: # Builds images - mandatory: NAME=[name]
	task_type=$$(make task-type NAME=$(NAME))
	rm -rf $(DOCKER_DIR)/task/assets/*
	rm -rf $(DOCKER_DIR)/task/Dockerfile.effective
	rm -rf $(DOCKER_DIR)/task/.version
	mkdir $(DOCKER_DIR)/task/assets/utilities
	cp -r $(APPLICATION_DIR)/$$task_type/$(NAME)/*.py $(DOCKER_DIR)/task/assets/
	cp -r $(APPLICATION_DIR)/$$task_type/$(NAME)/requirements.txt $(DOCKER_DIR)/task/assets/
	cp -r $(APPLICATION_DIR)/utilities/*.py $(DOCKER_DIR)/task/assets/utilities/
	make docker-image NAME=$$task_type-$(NAME)
	rm -rf $(DOCKER_DIR)/task/assets/*

start: project-start # Start project

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

test: # Test project
	make start
	make stop

push: # Push project artefacts to the registry - mandatory: TASK=[task]
	eval "$$(make aws-assume-role-export-variables)"
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			make docker-push NAME=$$task_type-$$task AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		task_type=$$(make task-type NAME=$(TASK))
		make docker-push NAME=$$task_type-$(TASK) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi

provision: # Provision environment - mandatory: PROFILE=[name], TASK=[task]
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-apply-auto-approve STACK=$(STACKS) PROFILE=$(PROFILE)
	if [ "$(TASK)" == "all" ]; then
		make terraform-apply-auto-approve STACK=$(TASKS) PROFILE=$(PROFILE)
	else
		make terraform-apply-auto-approve STACK=$(TASK) PROFILE=$(PROFILE)
	fi

plan: # Plan environment - mandatory: PROFILE=[name], TASK=[hk task]
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-plan STACK=$(STACKS) PROFILE=$(PROFILE)
	if [ "$(TASK)" == "all" ]; then
		make terraform-plan STACK=$(TASKS) PROFILE=$(PROFILE)
	else
		make terraform-plan STACK=$(TASK) PROFILE=$(PROFILE)
	fi

unit-test: # Runs unit tests for task - mandatory: TASK=[task]
	make unit-test-utilities
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make unit-test-task TASK="$$task"
		done
	else
		make unit-test-task TASK=$(TASK)
	fi

clean: # Clean up project
	make docker-network-remove

# --------------------------------------

build-tester: # Builds image used for testing - mandatory: PROFILE=[name]
	make docker-image NAME=tester

push-tester: # Pushes image used for testing - mandatory: PROFILE=[name]
	make docker-push NAME=tester


unit-test-task: # Run task unit tests - mandatory: TASK=[name of task]
	task_type=$$(make task-type NAME=$(TASK))
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	mkdir $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	mkdir $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	cp $(APPLICATION_TEST_DIR)/unit/$$task_type/$(TASK)/* $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	cp $(APPLICATION_DIR)/utilities/*.py $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	make docker-run-tools IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=application/$$task_type/$(TASK) \
		CMD="python3 -m pytest test/"
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities


unit-test-utilities: # Run utilities unit tests
	rm -rf $(APPLICATION_DIR)/utilities/test
	mkdir $(APPLICATION_DIR)/utilities/test
	cp $(APPLICATION_TEST_DIR)/unit/utilities/* $(APPLICATION_DIR)/utilities/test
	make docker-run-tools IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=application \
		CMD="python3 -m pytest utilities/test/"
	rm -rf $(APPLICATION_DIR)/utilities/test

coverage: ## Run test coverage - mandatory: PROFILE=[profile] TASK=[task] FORMAT=[xml/html]
	if [ "$(TASK)" = "" ]; then
		tasks=$(TASKS)
	else
		tasks=$(TASK)
	fi
	pythonpath=/tmp/.packages:/project/application/utilities
	for task in $$(echo $$tasks | tr "," "\n"); do
		task_type=$$(make task-type NAME=$$task)
		pythonpath+=:/project/application/$$task_type/
		rm -rf $(APPLICATION_DIR)/$$task_type/$$task/test
		rm -rf $(APPLICATION_DIR)/$$task_type/$$task/utilities
		mkdir $(APPLICATION_DIR)/$$task_type/$$task/test
		mkdir $(APPLICATION_DIR)/$$task_type/$$task/utilities
		cp $(APPLICATION_TEST_DIR)/unit/$$task_type/$$task/* $(APPLICATION_DIR)/$$task_type/$$task/test
		cp $(APPLICATION_DIR)/utilities/*.py $(APPLICATION_DIR)/$$task_type/$$task/utilities
	done
	rm -rf $(APPLICATION_DIR)/utilities/test
	mkdir $(APPLICATION_DIR)/utilities/test
	cp $(APPLICATION_TEST_DIR)/unit/utilities/* $(APPLICATION_DIR)/utilities/test
	make python-code-coverage-format IMAGE=$$(make _docker-get-reg)/tester:latest \
		EXCLUDE=*/test/*,hk/*/utilities/*,cron/*/utilities/* \
		ARGS="--env TASK=utilities --env SLACK_WEBHOOK_URL=https://slackmockurl.com/ --env PROFILE=local \
			--env PYTHONPATH=$$pythonpath"
	for task in $$(echo $$tasks | tr "," "\n"); do
		task_type=$$(make task-type NAME=$$task)
		rm -rf $(APPLICATION_DIR)/$$task_type/$$task/test
		rm -rf $(APPLICATION_DIR)/$$task_type/$$task/utilities
	done
	rm -rf $(APPLICATION_DIR)/utilities/test

python-code-coverage-format: ### Test Python code with 'coverage' - mandatory: CMD=[test program]; optional: DIR,FILES=[file or pattern],EXCLUDE=[comma-separated list],FORMAT=[xml,html]
	if [ "$(FORMAT)" = "" ]; then
		format=xml
	else
		format=$(FORMAT)
	fi
	make docker-run-tools SH=y DIR=$(or $(DIR), $(APPLICATION_DIR_REL)) ARGS="$(ARGS)" CMD=" \
		python -m coverage run \
			--source=$(or $(FILES), '.') \
			--omit=*/tests/*,$(EXCLUDE) \
			$(or $(CMD), -m pytest) && \
		python -m coverage $$(echo $$format | tr "," "\n") \
	"

# --------------------------------------

deployment-summary: # Returns a deployment summary
	echo Terraform Changes
	cat /tmp/terraform_changes.txt | grep -E 'Apply...'

pipeline-send-notification: ## Send Slack notification with the pipeline status - mandatory: PIPELINE_NAME,BUILD_STATUS
	eval "$$(make aws-assume-role-export-variables)"
	eval "$$(make secret-fetch-and-export-variables NAME=$(DEPLOYMENT_SECRETS))"
	make slack-it

propagate: # Propagate the image to production ecr - mandatory: BUILD_COMMIT_HASH=[image hash],GIT_TAG=[git tag],ARTEFACTS=[comma separated list]
	eval "$$(make aws-assume-role-export-variables PROFILE=$(PROFILE))"
	if [ "$(ARTEFACTS)" == "all" ]; then
		for image in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=$$task_type-$$image TAG=$(GIT_TAG) AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		task_type=$$(make task-type NAME=$$task)
		make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=$$task_type-$(ARTEFACTS) TAG=$(GIT_TAG) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi
parse-profile-from-tag: # Return profile based off of git tag - Mandatory GIT_TAG=[git tag]
	echo $(GIT_TAG) | cut -d "-" -f2

tag: # Tag commit for production deployment as `[YYYYmmddHHMMSS]-[env]` - mandatory: PROFILE=[profile name],COMMIT=[hash]
	hash=$$(make git-hash COMMIT=$(COMMIT))
	make git-tag-create-environment-deployment PROFILE=$(PROFILE) COMMIT=$$hash

task-type: # Return the type of task cron/hk - mandatory: NAME=[name of task]
	if [ -d $(APPLICATION_DIR)/hk/$(NAME) ]; then
		echo hk
	elif [ -d $(APPLICATION_DIR)/cron/$(NAME) ]; then
		echo cron
	else
		exit 1
	fi

# ==============================================================================
# Supporting targets

trust-certificate: ssl-trust-certificate-project ## Trust the SSL development certificate

create-artefact-repositories: # Create ECR repositories to store the artefacts - mandatory: AWS_ACCOUNT=[account]
	make docker-create-repository NAME=hk-filter
	make docker-create-repository NAME=hk-referralroles
	make docker-create-repository NAME=hk-symptomdiscrimintators

create-tester-repository: # Create ECR repositories to store the artefacts
	make docker-create-repository NAME=tester

# ==============================================================================

.SILENT: \
	task-type
