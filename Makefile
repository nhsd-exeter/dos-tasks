
PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

edit-environment-variable: ## update placeholder value for cron job target database Mandatory [DB_NAME] [TASK]
	echo "Updating environment variable to $(DB_NAME) for $(TASK)"
	sed "s/DB_NAME_TO_REPLACE/$(DB_NAME)/g" $(TERRAFORM_DIR)/$(STACK)/$(TASK)/template/main.tf  > \
			$(TERRAFORM_DIR)/$(STACK)/$(TASK)/main.tf

set-database-for-cron-jobs: ## update db-name for cron tasks only mandatory: TASK=[task] DB_NAME=[db name minus prefix eg test not pathwaysdos-test]
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$$task_type" == 'cron' ]; then
		make edit-environment-variable DB_NAME=$(DB_NAME)
	else
		echo "$(TASK) is not a recognised cron job. Nothing to do"
	fi

#==========================
build: # Build project - mandatory: TASK=[task]
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make build-image NAME=$$task
		done
	else
		make build-image NAME=$(TASK)
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
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			make docker-push NAME=$$task_type-$$task
		done
	else
		task_type=$$(make task-type NAME=$(TASK))
		make docker-push NAME=$$task_type-$(TASK)
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

# eg make destroy PROFILE=nonprod TASK=symptomgroups
destroy-hk: # Destroy housekeeping lambda - mandatory: PROFILE=[name], TASK=[hk task]
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$$task_type" == 'hk' ]; then
		eval "$$(make secret-fetch-and-export-variables)"
		if [ "$(TASK)" == "all" ]; then
			echo do nothing for now
			# make terraform-plan STACK=$(TASKS) PROFILE=$(PROFILE)
		else
			make terraform-destroy STACK=$(TASK) PROFILE=$(PROFILE)
		fi
	else
		echo $(TASK) is not an hk job
	fi

# make destroy-all-cron PROFILE=nonprod
destroy-all-cron: ## Clear down every cron for every db - mandatory [PROFILE]
	for task in $$(echo $(TASKS) | tr "," "\n"); do
		task_type=$$(make task-type NAME=$$task)
		if [ "$$task_type" == 'cron' ]; then
			make destroy-cron-for_database PROFILE=$(PROFILE) TASK=$$task
		else
			echo "Only clearing down cron jobs and $$task is not a cron job"
		fi
	done

destroy-cron-for_database: ## iterate over all dbs for cron task - mandatory [PROFILE] [TASK]
	for db_name in $$(echo $(ENVIRONMENT_LIST) | tr "," "\n" | tr -d []); do
		make destroy-cron PROFILE=$(PROFILE) TASK=$(TASK) DB_NAME=$$db_name
	done

# eg make destroy-cron PROFILE=nonprod TASK=ragreset DB_NAME=teamb
destroy-cron: # Destroy environment - mandatory: PROFILE=[name], TASK=[hk task] [DB_NAME]
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$$task_type" == 'cron' ]; then
		echo "Clearing down the $(PROFILE) $(TASK) lambda for the $(DB_NAME) database"
		eval "$$(make secret-fetch-and-export-variables)"
		make set-database-for-cron-jobs TASK=$(TASK) DB_NAME=$(DB_NAME)
		make terraform-destroy STACK=$(TASK) PROFILE=$(PROFILE)
	else
		echo $(TASK) is not a cron job
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
remove-old-versions-for-task: ## Prune old versions of hk and/or cron lambdas - Mandatory; [PROFILE] - Optional [TASK] [DB_NAME]
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			if [ $$task_type == "hk" ]; then
				make remove-old-versions-for-hk-task PROFILE=$(PROFILE) TASK=$$task
			fi
			if [ $$task_type == "cron" ]; then
				make remove-old-versions-for-cron-task PROFILE=$(PROFILE) TASK=$$task DB_NAME=$(DB_NAME)
			fi
		done
	else
			task_type=$$(make task-type NAME=$(TASK))
			if [ $$task_type == "hk" ]; then
				make remove-old-versions-for-hk-task PROFILE=$(PROFILE) TASK=$(TASK)
			fi
			if [ $$task_type == "cron" ]; then
				make remove-old-versions-for-cron-task PROFILE=$(PROFILE) TASK=$(TASK) DB_NAME=$(DB_NAME)
			fi
	fi


remove-old-versions-for-hk-task: ## Prune old versions of hk task lambdas - Mandatory; [PROFILE] [TASK]
	eval "$$(make aws-assume-role-export-variables)"
	task_type=$$(make task-type NAME=$(TASK))
	lambda_name="${SERVICE_PREFIX}-$$task_type-$(TASK)-lambda"
	echo "Checking for older versions of hk lambda function $$lambda_name"
	make aws-lambda-remove-old-versions NAME=$$lambda_name

remove-old-versions-for-cron-task: ## Prune old versions of cron lambdas - Mandatory; [PROFILE] [TASK] [DB_NAME]
	eval "$$(make aws-assume-role-export-variables)"
	task_type=$$(make task-type NAME=$(TASK))
	lambda_name="${SERVICE_PREFIX}-$$task_type-$(TASK)-$(DB_NAME)-lambda"
	echo "Checking for older versions of cron lambda function $$lambda_name"
	make aws-lambda-remove-old-versions NAME=$$lambda_name

aws-lambda-remove-old-versions: ## Remove older versions Mandatory NAME=[lambda function] Optional LAMBDA_VERSIONS_TO_RETAIN (default 5)
	older_versions_to_remove="$$(make aws-lambda-get-versions-to-remove NAME=$(NAME))"
	# convert space separated string into array
	version_array=($$older_versions_to_remove)
	echo "There are $${#version_array[*]} versions to be removed for $(NAME)"
	for version in $${older_versions_to_remove}
		do
			make aws-lamba-function-delete NAME=$(NAME) VERSION=$$version
		done

aws-lamba-function-delete: ## Delete version of lambda function - Mandatory NAME=[lambda function] VERSION=[version number]
	echo "Removing version $(VERSION) for $(NAME)"
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) lambda delete-function \
			--function-name $(NAME) \
			--qualifier $(VERSION) \
		"

aws-lambda-get-versions-to-remove: ## Returns list of version ids for a lambda function that can be removed - Mandatory NAME=[lambda function name] - Optional LAMBDA_VERSIONS_TO_RETAIN (default 5)
	versions="$$(make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) lambda list-versions-by-function \
			--function-name $(NAME) \
			--output text --query 'Versions[*].Version'  \
		")"
		if [ $(LAMBDA_VERSIONS_TO_RETAIN) -lt 5 ]; then
				retain_number=5
		else
				retain_number=$(LAMBDA_VERSIONS_TO_RETAIN)
		fi
		version_array=($$versions)
		# Latest is included in array but protected so need to reduce size of array by 1
		number_to_remove=$$(($${#version_array[*]}-1-$$retain_number))
		versions_to_remove=()
		count=0
		if [ $$number_to_remove -gt 0 ] ; then
			for version in $${version_array[*]}
				do
					if [[ $$version != *"LATEST" ]]; then
						count=$$((count + 1))
						versions_to_remove+=("$$version")
					fi
					if [ $$count -eq $$number_to_remove ]; then
						break
					fi
				done
		fi
		echo $${versions_to_remove[*]}

# --------------------------------------

deployment-summary: # Returns a deployment summary
	echo Terraform Changes
	cat /tmp/terraform_changes.txt | grep -E 'Apply...'

pipeline-send-notification: ## Send Slack notification with the pipeline status - mandatory: PIPELINE_NAME,BUILD_STATUS
	eval "$$(make aws-assume-role-export-variables)"
	eval "$$(make secret-fetch-and-export-variables NAME=$(DEPLOYMENT_SECRETS))"
	make slack-it

propagate: # Propagate the image to production ecr - mandatory: BUILD_COMMIT_HASH=[image hash],GIT_TAG=[git tag],ARTEFACTS=[comma separated list]
	if [ "$(ARTEFACTS)" == "all" ]; then
		for image in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=$$task_type-$$image TAG=$(GIT_TAG)
		done
	else
		task_type=$$(make task-type NAME=$$task)
		make docker-image-find-and-version-as COMMIT=$(BUILD_COMMIT_HASH) NAME=$$task_type-$(ARTEFACTS) TAG=$(GIT_TAG)
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
	make docker-create-repository NAME=hk-symptomdiscriminators
	make docker-create-repository NAME=hk-symptomgroups
	make docker-create-repository NAME=cron-ragreset

create-tester-repository: # Create ECR repositories to store the artefacts
	make docker-create-repository NAME=tester

# ==============================================================================

.SILENT: \
	aws-lambda-get-versions-to-remove \
	parse-profile-from-tag \
	cron-task-check \
	task-type
