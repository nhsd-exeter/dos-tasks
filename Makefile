PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

build: project-config # Build project - mandatory: TASK=[hk task]
	make docker-build NAME=hk-filter
	if [ $(TASK) == 'all' ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make build-image NAME="hk-$$task" AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		make build-image NAME=hk-$(TASK) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi

build-image: # TODO: fill out generic build process for images | Builds images - mandatory: NAME=[hk name]
	rm -rf $(DOCKER_DIR)/hk/assets/*
	cp -r $(APPLICATION_DIR)/$(NAME) $(DOCKER_DIR)/hk/assets/
	make docker-build NAME=hk-$(NAME)
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
	make docker-push NAME=hk-filter
	if [ $(TASK) == 'all' ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make docker-push NAME="hk-$$task" AWS_ECR=$(AWS_LAMBDA_ECR)
		done
	else
		make docker-push NAME=hk-$(TASK) AWS_ECR=$(AWS_LAMBDA_ECR)
	fi

provision: # Provision environment - mandatory: PROFILE=[name], TASK=[hk task]
	eval "$$(make secret-fetch-and-export-variables)"
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

# --------------------------------------

lambda-alias: ### Updates new lambda version with alias based on commit hash - Mandatory PROFILE=[profile]
	eval "$$(make aws-assume-role-export-variables)"
	function=$(SERVICE_PREFIX)-rd-lambda
	versions=$$(make -s aws-lambda-get-latest-version NAME=$$function)
	version=$$(echo $$versions | make -s docker-run-tools CMD="jq '.Versions[-1].Version'" | tr -d '"')
	make aws-lambda-create-alias NAME=$$function VERSION=$$version

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
	for image in $$(echo $(or $(ARTEFACTS), $(ARTEFACT)) | tr "," "\n"); do
		make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=$$image TAG=$(GIT_TAG) AWS_ECR=$(AWS_LAMBDA_ECR)
	done

parse-profile-from-tag: # Return profile based off of git tag - Mandatory GIT_TAG=[git tag]
	echo $(GIT_TAG) | cut -d "-" -f2

tag: # Tag commit for production deployment as `[YYYYmmddHHMMSS]-[env]` - mandatory: PROFILE=[profile name],COMMIT=[hash]
	hash=$$(make git-hash COMMIT=$(COMMIT))
	make git-tag-create-environment-deployment PROFILE=$(PROFILE) COMMIT=$$hash

# ==============================================================================
# Supporting targets

trust-certificate: ssl-trust-certificate-project ## Trust the SSL development certificate

create-artefact-repositories: # Create ECR repositories to store the artefacts - mandatory: AWS_ACCOUNT=[account]
	make docker-create-repositories NAME=hk-filter
	make docker-create-repositories NAME=hk-referralroles

# ==============================================================================

.SILENT:
