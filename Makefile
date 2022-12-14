
PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
include $(abspath $(PROJECT_DIR)/build/automation/init.mk)

# ==============================================================================
# Development workflow targets

copy-cron-template-stack: ## update placeholder value for cron job target database Mandatory [DB_NAME] [TASK]
	echo "Updating environment variable to $(DB_NAME) for $(TASK)"
	rm -rf  $(TERRAFORM_DIR)/$(STACK)/$(TASK)-$(DB_NAME)
	mkdir $(TERRAFORM_DIR)/$(STACK)/$(TASK)-$(DB_NAME)
	sed "s/DB_NAME_TO_REPLACE/$(DB_NAME)/g" $(TERRAFORM_DIR)/$(STACK)/cron-template/$(TASK)/template/main.tf  > \
			$(TERRAFORM_DIR)/$(STACK)/cron-template/$(TASK)/main.tf
	cp $(TERRAFORM_DIR)/$(STACK)/cron-template/$(TASK)/*.tf $(TERRAFORM_DIR)/$(STACK)/$(TASK)-$(DB_NAME)


build-stack-for-cron-job: ## create a stack for cron and db - cron tasks only mandatory: TASK=[task] DB_NAME=[db name minus prefix eg test not pathwaysdos-test]
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$$task_type" == 'cron' ]; then
		make copy-cron-template-stack DB_NAME=$(DB_NAME)
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
	if [ "$(NAME)" == "integration" ]; then
		make build-hk-integration-tester-image NAME=$(NAME)
	else
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
	fi

start: project-start # Start project

stop: project-stop # Stop project

restart: stop start # Restart project

log: project-log # Show project logs

test: # Test project
	make start
	make stop

# Push targets
push: # Push project artefacts to the registry - mandatory: TASK=[task]
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			make push-image TASK=$$task
		done
	else
		make push-image TASK=$(TASK)
	fi

push-image: # Push project artefact to the registry - mandatory: TASK=[task]
	if [ "$(TASK)" == "integration" ]; then
		make push-hk-integration-tester-image
	else
		task_type=$$(make task-type NAME=$(TASK))
		make docker-push NAME=$$task_type-$(TASK)
	fi

# Provision targets
provision: ## provision resources for hk and cron - mandatory PROFILE TASK  and DB_NAME (cron only)
	make copy-temp-integration-test-files
	make terraform-apply-auto-approve STACK=$(STACKS) PROFILE=$(PROFILE)
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make provision-cron PROFILE=$(PROFILE) TASK=$$task DB_NAME=$(DB_NAME)
			else
				echo "$$task is not a cron job or no database specified for cron job"
			fi
			if [ "$$task_type" == 'hk' ]; then
				make provision-hk PROFILE=$(PROFILE) TASK=$$task
			fi
		done
	else
		task_type=$$(make task-type NAME=$(TASK))
		if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make provision-cron PROFILE=$(PROFILE) TASK=$(TASK) DB_NAME=$(DB_NAME)
		else
				echo "No database specified for cron job"
		fi
		if [ "$$task_type" == 'hk' ]; then
			make provision-hk PROFILE=$(PROFILE) TASK=$(TASK)
		fi
	fi
	make remove-temp-integration-test-files

provision-hk: ## Provision environment - mandatory: PROFILE=[name], TASK=[task]
	eval "$$(make secret-fetch-and-export-variables)"
	echo "Provisioning $(PROFILE) lambda for hk task $(TASK)"
	if [ "$(TASK)" == 'integration' ]; then
		make provision-hk-integration-tester STACK=integration-test
	else
		make terraform-apply-auto-approve STACK=$(TASK) PROFILE=$(PROFILE)
	fi

provision-cron: ## cron specific version of provision PROFILE TASK DB_NAME
	echo "Provisioning $(PROFILE) lambda $(TASK)-$(DB_NAME) for cron job"
	make build-stack-for-cron-job TASK=$(TASK) DB_NAME=$(DB_NAME)
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-apply-auto-approve STACK=$(TASK)-$(DB_NAME) PROFILE=$(PROFILE)
	make delete-stack-for-cron-job TASK=$(TASK) DB_NAME=$(DB_NAME)

provision-stacks: ## Provision environment - mandatory: PROFILE=[name]
	echo "Provisioning stack infrastrucure for $(PROFILE)"
	make terraform-apply-auto-approve STACK=$(STACKS) PROFILE=$(PROFILE)

# Plan targets
plan: # Plan cron and hk lambdas - mandatory: PROFILE=[name], TASK=[hk task] DB_NAME
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-plan STACK=$(STACKS) PROFILE=$(PROFILE)
	make copy-temp-integration-test-files
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make plan-cron PROFILE=$(PROFILE) TASK=$$task DB_NAME=$(DB_NAME)
			else
				echo "$$task is not a cron job or no database specified for cron job"
			fi
			if [ "$$task_type" == 'hk' ]; then
				make plan-hk PROFILE=$(PROFILE) TASK=$$task
			fi
		done
	else
		task_type=$$(make task-type NAME=$(TASK))
		if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make plan-cron PROFILE=$(PROFILE) TASK=$(TASK) DB_NAME=$(DB_NAME)
		else
				echo "No database specified for cron job"
		fi
		if [ "$$task_type" == 'hk' ]; then
			make plan-hk PROFILE=$(PROFILE) TASK=$(TASK)
		fi
	fi
	make remove-temp-integration-test-files

plan-hk: # Plan housekeeping lambda - mandatory: PROFILE=[name], TASK=[hk task]
	echo "Planning for hk task $(TASK)"
	eval "$$(make secret-fetch-and-export-variables)"
	if [ "$(TASK)" == 'integration' ]; then
			make plan-hk-integration-tester STACK=integration-test PROFILE=$(PROFILE)
	else
			make terraform-plan STACK=$(TASK) PROFILE=$(PROFILE)
	fi

plan-cron: # Plan cron job - mandatory: PROFILE=[name], TASK=[hk task] DB_NAME
	echo "Planning for cron job $(TASK)-$(DB_NAME)"
	make build-stack-for-cron-job TASK=$(TASK) DB_NAME=$(DB_NAME)
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-plan STACK=$(TASK)-$(DB_NAME) PROFILE=$(PROFILE)
	make delete-stack-for-cron-job TASK=$(TASK) DB_NAME=$(DB_NAME)

plan-stacks: ### plan shared infrastructure defined in STACKS PROFILE
	make terraform-plan-detailed STACK=$(STACKS) PROFILE=$(PROFILE)

#  Destroy targets
destroy: # To destroy cron and hk lambdas - mandatory: PROFILE=[name], TASK=[hk task] DB_NAME
	make copy-temp-integration-test-files
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make destroy-cron PROFILE=$(PROFILE) TASK=$$task DB_NAME=$(DB_NAME)
			else
				echo "No database specified for cron job"
			fi
			if [ "$$task_type" == 'hk' ]; then
				make destroy-hk PROFILE=$(PROFILE) TASK=$$task
			fi
		done
	else
		task_type=$$(make task-type NAME=$(TASK))
		if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make destroy-cron PROFILE=$(PROFILE) TASK=$(TASK) DB_NAME=$(DB_NAME)
		else
				echo "No database specified for cron job"
		fi
		if [ "$$task_type" == 'hk' ]; then
			make destroy-hk PROFILE=$(PROFILE) TASK=$(TASK)
		fi
	fi
	make remove-temp-integration-test-files

# eg make destroy PROFILE=nonprod TASK=symptomgroups
destroy-hk: # Destroy housekeeping lambda - mandatory: PROFILE=[name], TASK=[hk task]
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$$task_type" == 'hk' ]; then
		eval "$$(make secret-fetch-and-export-variables)"
		if [ "$(TASK)" == 'integration' ]; then
			make destroy-hk-integration-tester STACK=integration-test PROFILE=$(PROFILE)
		else
			make terraform-destroy-auto-approve STACK=$(TASK) PROFILE=$(PROFILE)
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
			echo "Task $$task is not a cron job"
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
		make build-stack-for-cron-job TASK=$(TASK) DB_NAME=$(DB_NAME)
		make terraform-destroy-auto-approve STACK=$(TASK)-$(DB_NAME) PROFILE=$(PROFILE)
		make delete-stack-for-cron-job TASK=$(TASK) DB_NAME=$(DB_NAME)
	else
		echo $(TASK) is not a cron job
	fi

delete-stack-for-cron-job: ## create a stack for cron and db - cron tasks only mandatory: TASK=[task] DB_NAME=[db name minus prefix eg test not pathwaysdos-test]
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$$task_type" == 'cron' ]; then
		rm -r $(TERRAFORM_DIR)/$(STACK)/$(TASK)-$(DB_NAME)
	else
		echo "$(TASK) is not a recognised cron job. Nothing to do"
	fi

# ----------

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

poll-s3-for-file: ## retries look up for file in bucket [MAX_ATTEMPTS] mandatory [BUCKET] [FILENAME]
	echo "Checking bucket $(BUCKET) for file $(FILENAME)"
	eval "$$(make aws-assume-role-export-variables)"
	for i in {1..$(MAX_ATTEMPTS)}
	do
		archived=$$(make check-bucket-for-file BUCKET=$(BUCKET) FILENAME=$(FILENAME))
		echo $$archived
		if [ $$archived == true ]; then
			break
		fi
		echo Sleeping..
		sleep 1
	done

check-bucket-for-file: ## returns true if filename exists in bucket  - mandatory [BUCKET] [ENV] [FILENAME]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3 ls \
			s3://$(BUCKET)/ \
			2>&1 | grep -q $(FILENAME) \
	" > /dev/null 2>&1 && echo true || echo false

build-tester: # Builds image used for testing - mandatory: PROFILE=[name]
	mkdir $(DOCKER_DIR)/tester/assets/integration
	mkdir $(DOCKER_DIR)/tester/assets/integration/data-files
	cp $(APPLICATION_TEST_DIR)/integration/data-files/* $(DOCKER_DIR)/tester/assets/integration/data-files
	make docker-image NAME=tester

push-tester: # Pushes image used for testing - mandatory: PROFILE=[name]
	make docker-push NAME=tester

copy-stt-unit-test-files:
	rm -rf $(APPLICATION_DIR)/hk/stt/test-files
	mkdir $(APPLICATION_DIR)/hk/stt/test-files
	cp $(APPLICATION_TEST_DIR)/stt-test-files/* $(APPLICATION_DIR)/hk/stt/test-files

remove-temp-stt-unit-test-files:
	rm -rf $(APPLICATION_DIR)/hk/stt/test-files

unit-test-task: # Run task unit tests - mandatory: TASK=[name of task]
	if [ "$(TASK)" = "stt" ]; then
		make remove-temp-stt-unit-test-files
		make copy-stt-unit-test-files
	fi
	if [ "$(TASK)" = "integration" ]; then
		make remove-temp-hk-integration-test-files
		make create-temp-hk-integration-test-files
	fi
	task_type=$$(make task-type NAME=$(TASK))
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	mkdir $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	cp $(APPLICATION_TEST_DIR)/unit/$$task_type/$(TASK)/* $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	mkdir $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	cp $(APPLICATION_DIR)/utilities/*.py $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	if [ "$(TASK)" = "integration" ]; then
		mkdir $(APPLICATION_DIR)/$$task_type/$(TASK)/models
		cp $(APPLICATION_DIR)/models/*.py $(APPLICATION_DIR)/$$task_type/$(TASK)/models
	fi
	make docker-run-tools IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=application/$$task_type/$(TASK) \
		CMD="python3 -m pytest test/"
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/test
	rm -rf $(APPLICATION_DIR)/$$task_type/$(TASK)/utilities
	if [ "$(TASK)" = "stt" ]; then
		make remove-temp-stt-unit-test-files
	fi
	if [ "$(TASK)" = "integration" ]; then
		make remove-temp-hk-integration-test-files
	fi

unit-test-utilities: # Run utilities unit tests
	rm -rf $(APPLICATION_DIR)/test-files
	rm -rf $(APPLICATION_DIR)/utilities/test
	mkdir $(APPLICATION_DIR)/utilities/test
	mkdir $(APPLICATION_DIR)/test-files
	cp $(APPLICATION_TEST_DIR)/stt-test-files/* $(APPLICATION_DIR)/test-files
	cp $(APPLICATION_TEST_DIR)/unit/utilities/* $(APPLICATION_DIR)/utilities/test
	make docker-run-tools IMAGE=$$(make _docker-get-reg)/tester:latest \
		DIR=application \
		CMD="python3 -m pytest utilities/test/"
	rm -rf $(APPLICATION_DIR)/utilities/test
	rm -rf $(APPLICATION_DIR)/test-files

copy-stt-coverage-test-files:
	rm -rf $(APPLICATION_DIR)/test-files
	mkdir $(APPLICATION_DIR)/test-files
	cp $(APPLICATION_TEST_DIR)/stt-test-files/* $(APPLICATION_DIR)/test-files

remove-temp-stt-coverage-test-files:
	rm -rf $(APPLICATION_DIR)/test-files

coverage: ## Run test coverage - mandatory: PROFILE=[profile] TASK=[task] FORMAT=[xml/html]
	make copy-stt-coverage-test-files
	make remove-temp-hk-integration-test-files
	make create-temp-hk-integration-test-files
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
	make remove-temp-stt-coverage-test-files
	make remove-temp-hk-integration-test-files

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
			if [ $$task_type == "cron" ] && [ ! -z "$(DB_NAME)" ]; then
				make remove-old-versions-for-cron-task PROFILE=$(PROFILE) TASK=$$task DB_NAME=$(DB_NAME)
			else
				echo "DB_NAME parameter required to remove older cron job versions"
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
			make aws-lamba-function-delete-versions NAME=$(NAME) VERSION=$$version
		done

aws-lamba-function-delete-versions: ## Delete version of lambda function - Mandatory NAME=[lambda function] VERSION=[version number]
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

delete-lambdas-for-task: ## delete hk and/or cron lambdas - Mandatory; [PROFILE] - Optional [TASK] [DB_NAME]
	make copy-temp-integration-test-files
	if [ "$(TASK)" == "all" ]; then
		for task in $$(echo $(TASKS) | tr "," "\n"); do
			task_type=$$(make task-type NAME=$$task)
			if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
				make delete-lambdas-for-cron-task PROFILE=$(PROFILE) TASK=$$task DB_NAME=$(DB_NAME)
			else
				echo "$$task is not a cron job or no database specified for cron job"
			fi
			if [ "$$task_type" == 'hk' ]; then
				make delete-lambdas-for-hk-task PROFILE=$(PROFILE) TASK=$$task
			fi
		done
	else
		task_type=$$(make task-type NAME=$(TASK))
		if [ "$$task_type" == 'cron' ] && [ ! -z "$(DB_NAME)" ]; then
			make delete-lambdas-for-cron-task PROFILE=$(PROFILE) TASK=$(TASK) DB_NAME=$(DB_NAME)
		else
			echo "No database specified for cron job"
		fi
		if [ "$$task_type" == 'hk' ]; then
			make delete-lambdas-for-hk-task PROFILE=$(PROFILE) TASK=$(TASK)
		fi
	fi
	make remove-temp-integration-test-files

delete-lambdas-for-hk-task: ## Delete hk task lambdas - Mandatory; [PROFILE] [TASK]
	eval "$$(make aws-assume-role-export-variables)"
	task_type=$$(make task-type NAME=$(TASK))
	if [ "$(TASK)" == 'integration' ]; then
		lambda_name="${SERVICE_PREFIX}-$$task_type-$(TASK)-tester-lambda"
	else
		lambda_name="${SERVICE_PREFIX}-$$task_type-$(TASK)-lambda"
	fi
	echo "Checking for hk lambda function $$lambda_name"
	make aws-lambda-function-delete NAME=$$lambda_name

delete-lambdas-for-cron-task: ## Delete hk cron lambdas - Mandatory; [PROFILE] [TASK]
	eval "$$(make aws-assume-role-export-variables)"
	task_type=$$(make task-type NAME=$(TASK))
	lambda_name="${SERVICE_PREFIX}-$$task_type-$(TASK)-$(DB_NAME)-lambda"
	echo "Checking for cron lambda function $$lambda_name"
	make aws-lambda-function-delete NAME=$$lambda_name


check-lambda-exists: ## Checking lambda function exists - Mandatory NAME=[lambda function]
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) lambda get-function \
			--function-name $(NAME) \
	" > /dev/null 2>&1 && echo true || echo false

aws-lambda-function-delete: ## Delete of lambda function - Mandatory NAME=[lambda function]
	if [ "true" == "$$(make -s check-lambda-exists NAME=${NAME})" ] ; then
		echo "Removing lambda $(NAME)"
		make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
			$(AWSCLI) lambda delete-function \
				--function-name $(NAME) \
			"
	else
		echo "Lambda $(NAME) does not exist"
	fi
# --------------------------------------

deployment-summary: # Returns a deployment summary
	echo Terraform Changes
	cat /tmp/terraform_changes.txt | grep -E 'Apply...'

pipeline-send-failure-notification: ## Send Slack notification with the pipeline status - mandatory: PIPELINE_NAME,BUILD_STATUS
	make pipeline-send-notification DEPLOYMENT_SECRETS=$(SLACK_SECRETS)

pipeline-send-notification: ## Send Slack notification with the pipeline status - mandatory: PIPELINE_NAME,BUILD_STATUS optional:DEPLOYMENT_SECRETS
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
	make docker-create-repository NAME=hk-servicetypes
	make docker-create-repository NAME=hk-stt
	make docker-create-repository NAME=cron-ragreset
	make docker-create-repository NAME=cron-removeoldchanges
	make docker-create-repository NAME=hk-symptomdiscriminatorsynonyms
	make docker-create-repository NAME=hk-symptomgroupdiscriminators
	make docker-create-repository NAME=hk-integration-tester

create-tester-repository: # Create ECR repositories to store the artefacts
	make docker-create-repository NAME=tester

# ==============
# integration test related targets
# --------------------------------------
create-temp-hk-integration-test-files: # copy integration code from test/integration to new application/hk/integration folder
	rm -rf $(APPLICATION_DIR)/hk/integration/*
	mkdir $(APPLICATION_DIR)/hk/integration
	mkdir $(APPLICATION_DIR)/hk/integration/data-files
	mkdir $(APPLICATION_DIR)/hk/integration/test-files
	mkdir $(APPLICATION_DIR)/models
	cp $(APPLICATION_TEST_DIR)/integration/*.py $(APPLICATION_DIR)/hk/integration/
	cp $(APPLICATION_TEST_DIR)/integration/requirements.txt $(APPLICATION_DIR)/hk/integration/
	cp $(APPLICATION_TEST_DIR)/integration/models/* $(APPLICATION_DIR)/models
	cp $(APPLICATION_TEST_DIR)/integration/data-files/* $(APPLICATION_DIR)/hk/integration/data-files

remove-temp-hk-integration-test-files:
	rm -rf $(APPLICATION_DIR)/hk/integration
	rm -rf $(APPLICATION_DIR)/models

build-hk-integration-tester-image: # Builds integration test image [NAME]
	make remove-temp-hk-integration-test-files
	make create-temp-hk-integration-test-files
	task_type=$$(make task-type NAME=$(NAME))
	rm -rf $(DOCKER_DIR)/hk-integration-tester/assets/*
	rm -rf $(DOCKER_DIR)/hk-integration-tester/Dockerfile.effective
	rm -rf $(DOCKER_DIR)/hk-integration-tester/.version
	mkdir $(DOCKER_DIR)/hk-integration-tester/assets/utilities
	cp -r $(APPLICATION_DIR)/utilities/*.py $(DOCKER_DIR)/hk-integration-tester/assets/utilities/
	mkdir $(DOCKER_DIR)/hk-integration-tester/assets/models
	cp -r $(APPLICATION_DIR)/models/*.py $(DOCKER_DIR)/hk-integration-tester/assets/models/
	cp -r $(APPLICATION_DIR)/$$task_type/integration/*.py $(DOCKER_DIR)/hk-integration-tester/assets/
	cp -r $(APPLICATION_DIR)/$$task_type/integration/requirements.txt $(DOCKER_DIR)/hk-integration-tester/assets/
	cp -r $(APPLICATION_DIR)/$$task_type/integration/data-files/ $(DOCKER_DIR)/hk-integration-tester/assets/data-files
	make docker-image NAME=hk-integration-tester
	rm -rf $(DOCKER_DIR)/hk-integration-tester/assets/*
	make remove-temp-hk-integration-test-files

push-hk-integration-tester-image: #
	make docker-push NAME=hk-integration-tester

provision-hk-integration-tester: ## mandatory: PROFILE=[name], STACK=[integration-test]
	echo "Provisioning $(PROFILE) lambda for hk-integration tester"
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-apply-auto-approve STACK=$(STACK) PROFILE=$(PROFILE)

destroy-hk-integration-tester: ## mandatory: PROFILE=[name], STACK=[integration-test]
	echo "Destroying $(PROFILE) lambda for hk-integration tester"
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-destroy-auto-approve STACK=$(STACK) PROFILE=$(PROFILE)

plan-hk-integration-tester: ## mandatory: PROFILE=[name], STACK=[integration-test]
	echo "Planning $(PROFILE) lambda for $(STACK)"
	eval "$$(make secret-fetch-and-export-variables)"
	make terraform-plan STACK=$(STACK) PROFILE=$(PROFILE)

copy-temp-integration-test-files:
	rm -rf $(APPLICATION_DIR)/hk/integration
	mkdir $(APPLICATION_DIR)/hk/integration
	mkdir $(APPLICATION_DIR)/hk/integration/models
# mkdir $(APPLICATION_DIR)/hk/integration/test
	mkdir $(APPLICATION_DIR)/hk/integration/data-files
	mkdir $(APPLICATION_DIR)/hk/integration/utilities
	cp $(APPLICATION_DIR)/utilities/*.py $(APPLICATION_DIR)/hk/integration/utilities
	cp $(APPLICATION_TEST_DIR)/integration/*.py $(APPLICATION_DIR)/hk/integration
	cp $(APPLICATION_TEST_DIR)/integration/requirements.txt $(APPLICATION_DIR)/hk/integration
	cp $(APPLICATION_TEST_DIR)/integration/models/* $(APPLICATION_DIR)/hk/integration/models
# cp $(APPLICATION_TEST_DIR)/integration/test/* $(APPLICATION_DIR)/hk/integration/test
	cp $(APPLICATION_TEST_DIR)/integration/data-files/* $(APPLICATION_DIR)/hk/integration/data-files

remove-temp-integration-test-files:
	rm -rf $(APPLICATION_DIR)/hk/integration

#====
# targets to upload test files to s3 bucket and check in archive folder
#====
load-integration-test-files-to-s3:  ### Upload all test csv files to bucket - mandatory: FILEPATH=[local path (inside container)],BUCKET=[name of folder in bucket]
	eval "$$(make aws-assume-role-export-variables)"
	args="--recursive --include 'int_*.csv'"
	make aws-s3-upload FILE=$(FILEPATH) URI=$(BUCKET) ARGS=$$args

check-integration-test-files:## iterate over integration test folder mandatory: [MAX_ATTEMPTS]  BUCKET=[name of folder in bucket]
	int_test_folder="test/integration/test-files/*"
	for f in $$int_test_folder
	do
		filename=`basename "$$f"`
		make poll-s3-for-file MAX_ATTEMPTS=$(MAX_ATTEMPTS) BUCKET=$(BUCKET) FILENAME=$$filename
	done

load-single-integration-test-file-to-s3:  ### Upload single file to bucket - mandatory: FILENAME=[name of file],BUCKET=[name of folder in bucket]
	eval "$$(make aws-assume-role-export-variables)"
	path="test/integration/test-files"
	make aws-s3-upload FILE=$$path/$(FILENAME) URI=$(BUCKET)/$(FILENAME)

check-single-integration-test-file:## check if file has been archived mandatory: [MAX_ATTEMPTS]  BUCKET=[name of folder in bucket], FILENAME=[name of file]
	filename=`basename "$(FILENAME)"`
	make poll-s3-for-file MAX_ATTEMPTS=$(MAX_ATTEMPTS) BUCKET=$(BUCKET) FILENAME=$$filename

#============
# tidy up post testing
#==============

clear-integration-archive: # BUCKET=[name of folder in bucket]
	eval "$$(make aws-assume-role-export-variables)"
	make -s docker-run-tools ARGS="$$(echo $(AWSCLI) | grep awslocal > /dev/null 2>&1 && echo '--env LOCALSTACK_HOST=$(LOCALSTACK_HOST)' ||:)" CMD=" \
		$(AWSCLI) s3 rm s3://$(BUCKET)/archive/ --recursive --exclude '*' --include '*.csv'"

#=================
# targets to test results of hk job
#=================

invoke-test-check: ###Run hk integration test lambda to check result of task - Mandatory [PROFILE] [TASK]
	eval "$$(make aws-assume-role-export-variables)"
	aws lambda invoke --function-name $(TF_VAR_hk_integration_tester_lambda_function_name) \
	--payload '{ "task": "$(TASK)" }' \
	/dev/stdout

# lambda returns success flag and lambda status
# eg {"success": "False"}{ "StatusCode": 200, "ExecutedVersion": "$LATEST" }
run-integration-test-lambda: # extract the value of success - Mandatory [PROFILE] [TASK]
	lambda_result=$$(make invoke-test-check PROFILE=$(PROFILE) TASK=$(TASK))
	result_array=(`echo $$lambda_result | tr '}' ' '`)
	result=$${result_array[1]}
	result=$${result#?}
	result=$${result%?}
	if [ $$result == "True" ]; then
		echo pass
		exit 0
	else
		echo fail
		exit 1
	fi

# ==============================================================================

git-branch-format:  ## DOS version of [BRANCH_NAME]
	echo ${BRANCH_NAME} | sed 's;/;%2F;g'


.SILENT: \
	aws-lambda-get-versions-to-remove \
	parse-profile-from-tag \
	cron-task-check \
	check-bucket-for-file \
	poll-s3-for-file \
	task-type \
	invoke-test-check \
	git-branch-format
