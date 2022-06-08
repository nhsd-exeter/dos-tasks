
PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

build: # Build project - mandatory: TASK=[hk task]
	make build-image NAME=filter AWS_ECR=$(AWS_LAMBDA_ECR)
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make build-image NAME="$$task" AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		make build-image NAME=$(TASK) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi

build-image: # Builds images - mandatory: NAME=[hk name]
	rm -rf $(DOCKER_DIR)/hk/assets/*
	rm -rf $(DOCKER_DIR)/hk/Dockerfile.effective
	rm -rf $(DOCKER_DIR)/hk/.version
	mkdir $(DOCKER_DIR)/hk/assets/utilities
	cp -r $(APPLICATION_DIR)/hk/$(NAME)/*.py $(DOCKER_DIR)/hk/assets/
	cp -r $(APPLICATION_DIR)/hk/$(NAME)/requirements.txt $(DOCKER_DIR)/hk/assets/
	cp -r $(APPLICATION_DIR)/utilities/*.py $(DOCKER_DIR)/hk/assets/utilities/
	make docker-image NAME=hk-$(NAME)
	rm -rf $(DOCKER_DIR)/hk/assets/*

start: project-start # Start project

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

test: # Test project
	make start
	make stop

push: # Push project artefacts to the registry - mandatory: TASK=[hk task]
	eval "$$(make aws-assume-role-export-variables)"
	make docker-push NAME=hk-filter AWS_ECR=$(AWS_LAMBDA_ECR)
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make docker-push NAME="hk-$$task" AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		make docker-push NAME=hk-$(TASK) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi

provision: # Provision environment - mandatory: PROFILE=[name], TASK=[hk task]
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-apply-auto-approve STACK=$(STACKS) PROFILE=$(PROFILE)
	if [ "$(TASK)" == "all" ]; then
		make terraform-apply-auto-approve STACK=$(TASKS) PROFILE=$(PROFILE)
	else
		make terraform-apply-auto-approve STACK=$(TASK) PROFILE=$(PROFILE)
	fi

unit-test: # Runs unit tests for task - mandatory: TASK=[hk task]
	make unit-test-utilities
	make unit-test-task TASK=filter
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
	rm -rf $(APPLICATION_DIR)/hk/$(TASK)/test
	rm -rf $(APPLICATION_DIR)/hk/$(TASK)/utilities
	mkdir $(APPLICATION_DIR)/hk/$(TASK)/test
	mkdir $(APPLICATION_DIR)/hk/$(TASK)/utilities
	cp $(APPLICATION_TEST_DIR)/unit/hk-$(TASK)/* $(APPLICATION_DIR)/hk/$(TASK)/test
	cp $(APPLICATION_DIR)/utilities/*.py $(APPLICATION_DIR)/hk/$(TASK)/utilities
	make docker-run-tools IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=application/hk/$(TASK) \
		CMD="python3 -m pytest test/test_hk_$(TASK).py"
	rm -rf $(APPLICATION_DIR)/hk/$(TASK)/test
	rm -rf $(APPLICATION_DIR)/hk/$(TASK)/utilities


unit-test-utilities: # Run utilities unit tests
	rm -rf $(APPLICATION_DIR)/utilities/test
	mkdir $(APPLICATION_DIR)/utilities/test
	cp $(APPLICATION_TEST_DIR)/unit/utilities/* $(APPLICATION_DIR)/utilities/test
	make docker-run-tools IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=application \
		CMD="python3 -m pytest utilities/test/"
	rm -rf $(APPLICATION_DIR)/utilities/test

coverage: ## Run test coverage - mandatory: PROFILE=[profile] TASK=[task]
	if [ "$(TASK)" = "" ]; then
		tasks=$(TASKS),filter
	else
		tasks=$(TASK)
	fi
	pythonpath=/tmp/.packages:/project/application/utilities
	for task in $$(echo $$tasks | tr "," "\n"); do
		pythonpath+=:/project/application/hk/
		rm -rf $(APPLICATION_DIR)/hk/$$task/test
		rm -rf $(APPLICATION_DIR)/hk/$$task/utilities
		mkdir $(APPLICATION_DIR)/hk/$$task/test
		mkdir $(APPLICATION_DIR)/hk/$$task/utilities
		cp $(APPLICATION_TEST_DIR)/unit/hk-$$task/* $(APPLICATION_DIR)/hk/$$task/test
		cp $(APPLICATION_DIR)/utilities/*.py $(APPLICATION_DIR)/hk/$$task/utilities
	done
	rm -rf $(APPLICATION_DIR)/utilities/test
	mkdir $(APPLICATION_DIR)/utilities/test
	cp $(APPLICATION_TEST_DIR)/unit/utilities/* $(APPLICATION_DIR)/utilities/test
	make python-code-coverage IMAGE=$$(make _docker-get-reg)/tester:latest \
		EXCLUDE=*/test/*,hk/*/utilities/* \
		ARGS="--env TASK=utilities --env SLACK_WEBHOOK_URL=https://slackmockurl.com/ --env PROFILE=local \
			--env PYTHONPATH=$$pythonpath"
	for task in $$(echo $$tasks | tr "," "\n"); do
		rm -rf $(APPLICATION_DIR)/hk/$$task/test
		rm -rf $(APPLICATION_DIR)/hk/$$task/utilities
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
security-scan: ### Fetches container scan report and returns findings - Mandatory PROFILE=[profile], TASK=[hk task], TAG=[image tag]
	eval "$$(make aws-assume-role-export-variables)"
	scan=$$(make -s aws-describe-image-scan TASK=$(TASK) TAG=$(TAG))
	findings=$$(echo $$scan | make -s docker-run-tools CMD="jq '.imageScanFindings.findingSeverityCounts'" | tr -d '"')
	echo $$findings
	vulnerabilities=0
	for level in $$(echo $(VULNERABILITY_LEVEL) | tr "," "\n"); do
		if grep -q "$$level" <<< "$$findings"; then
			vulnerabilities=1
			break
		fi
	done
	if [ $$vulnerabilities -gt 0 ]; then
		echo false
	else
		echo true
	fi


aws-describe-image-scan: ### Describesr ECR image scan report - Mandatory PROFILE=[profile], TASK=[hk task], TAG=[image tag]
		make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) ecr describe-image-scan-findings \
			--repository-name $(PROJECT_GROUP_SHORT)/$(PROJECT_NAME_SHORT)/hk-$(TASK) \
			--image-id imageTag=$(TAG) \
			--output json \
		"

# --------------------------------------

lambda-alias: ### Updates new lambda version with alias based on commit hash - Mandatory PROFILE=[profile], TASK=[hk task]
	eval "$$(make aws-assume-role-export-variables)"
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			function=$(SERVICE_PREFIX)-hk-$$task-lambda
			versions=$$(make -s aws-lambda-get-latest-version NAME=$$function)
			version=$$(echo $$versions | make -s docker-run-tools CMD="jq '.Versions[-1].Version'" | tr -d '"')
			make aws-lambda-create-alias NAME=$$function VERSION=$$version
		done
	else
		function=$(SERVICE_PREFIX)-hk-$(TASK)-lambda
		versions=$$(make -s aws-lambda-get-latest-version NAME=$$function)
		version=$$(echo $$versions | make -s docker-run-tools CMD="jq '.Versions[-1].Version'" | tr -d '"')
		make aws-lambda-create-alias NAME=$$function VERSION=$$version
	fi

aws-lambda-get-latest-version: ### Fetches the latest function version for a lambda function - Mandatory NAME=[lambda function name]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) lambda list-versions-by-function \
			--function-name $(NAME) \
			--output json \
		"

aws-lambda-create-alias: ### Creates an alias for a lambda version - Mandatory NAME=[lambda function name], VERSION=[lambda version]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) lambda create-alias \
			--name $(VERSION)-$(BUILD_COMMIT_HASH) \
			--function-name $(NAME) \
			--function-version $(VERSION) \
		"

plan: # Provision environment - mandatory: PROFILE=[name], TASK=[hk task]
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-plan STACK=$(STACKS) PROFILE=$(PROFILE)
	if [ "$(TASK)" == "all" ]; then
		make terraform-plan STACK=$(TASKS) PROFILE=$(PROFILE)
	else
		make terraform-plan STACK=$(TASK) PROFILE=$(PROFILE)
	fi
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
	make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=hk-filter TAG=$(GIT_TAG) AWS_ECR=$(AWS_LAMBDA_ECR)
	if [ "$(ARTEFACTS)" == "all" ]; then
		for image in $$(echo $(TASKS) | tr "," "\n"); do
			make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=hk-$$image TAG=$(GIT_TAG) AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=hk-$(ARTEFACTS) TAG=$(GIT_TAG) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi
parse-profile-from-tag: # Return profile based off of git tag - Mandatory GIT_TAG=[git tag]
	echo $(GIT_TAG) | cut -d "-" -f2

tag: # Tag commit for production deployment as `[YYYYmmddHHMMSS]-[env]` - mandatory: PROFILE=[profile name],COMMIT=[hash]
	hash=$$(make git-hash COMMIT=$(COMMIT))
	make git-tag-create-environment-deployment PROFILE=$(PROFILE) COMMIT=$$hash

# ==============================================================================
# Supporting targets

trust-certificate: ssl-trust-certificate-project ## Trust the SSL development certificate

create-artefact-repositories: # Create ECR repositories to store the artefacts - mandatory: AWS_ACCOUNT=[account]
	make docker-create-repository NAME=hk-filter
	make docker-create-repository NAME=hk-referralroles

create-tester-repository: # Create ECR repositories to store the artefacts
	make docker-create-repository NAME=tester

# ==============================================================================

.SILENT:
