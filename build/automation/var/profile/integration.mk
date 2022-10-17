-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := integration
ENVIRONMENT := integration
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)
VULNERABILITY_LEVEL := CRITICAL,HIGH

# ==============================================================================
# Infrastructure variables

STACKS := secrets,s3,security-groups
# TODO check full list ,symptomdiscriminators,stt,symptomgroups,symptomdiscriminators
# don't need crons
TASKS := filter,integration,referralroles,symptomgroups,symptomdiscriminators,symptomdiscriminatorsynonyms,symptomgroupdiscriminators,servicetypes,stt
ENVIRONMENT_LIST := ["integration"]
TF_VAR_environment_list := $(ENVIRONMENT_LIST)

TF_VAR_deployment_secrets := $(DEPLOYMENT_SECRETS)
TF_VAR_image_version := $(or $(BUILD_TAG), latest)
TF_VAR_s3_tf_state_key := $(PROJECT_ID)/$(ENV)/s3/terraform.state
TF_VAR_security_groups_tf_state_key := $(PROJECT_ID)/$(ENV)/security-groups/terraform.state
TF_VAR_core_dos_db_sg := sg-05fdf44634b750fbd
TF_VAR_splunk_firehose_subscription := dos-cw-w-events-logs-firehose
TF_VAR_splunk_firehose_role := dos_cw_w_events_firehose_access_role

LAMBDA_VERSIONS_TO_RETAIN = 5

TF_VAR_hk_integration_tester_name = hk-integration-tester
TF_VAR_hk_integration_tester_lambda_function_name = $(PROJECT_ID)-$(ENV)-$(TF_VAR_hk_integration_tester_name)-lambda
# Lambda layer
TF_VAR_uec_dos_tasks_python_libs = uec-dos-tasks-python-libs
