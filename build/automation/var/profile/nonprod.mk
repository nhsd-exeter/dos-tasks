-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := nonprod
ENVIRONMENT := nonprod
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)
AWS_LAMBDA_ECR := $(or $(AWS_ACCOUNT_ID), 000000000000).dkr.ecr.$(AWS_DEFAULT_REGION).amazonaws.com
VULNERABILITY_LEVEL := CRITICAL,HIGH

# ==============================================================================
# Infrastructure variables

STACKS := secrets,s3,security-groups,filter
TASKS := referralroles
ENVIRONMENT_LIST := ["test","test1","test2","test3","test4","fix","performance","regression","teamb"]

TF_VAR_deployment_secrets := $(DEPLOYMENT_SECRETS)
TF_VAR_image_version := $(or $(BUILD_TAG), latest)
TF_VAR_s3_tf_state_key := $(PROJECT_ID)/$(ENV)/s3/terraform.state
TF_VAR_security_groups_tf_state_key := $(PROJECT_ID)/$(ENV)/security-groups/terraform.state
TF_VAR_core_dos_db_sg := sg-05fdf44634b750fbd
TF_VAR_splunk_firehose_subscription := dos-cw-w-events-logs-firehose
TF_VAR_splunk_firehose_role := dos_cw_w_events_firehose_access_role
