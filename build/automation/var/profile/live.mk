-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := live
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)

# ==============================================================================
# Infrastructure variables

STACKS := secrets,s3,security-groups
TASKS := filter,referralroles,symptomgroups,symptomdiscriminators
ENVIRONMENT_LIST := ["live"]
TF_VAR_environment_list := $(ENVIRONMENT_LIST)

TF_VAR_deployment_secrets := $(DEPLOYMENT_SECRETS)
TF_VAR_image_version := $(or $(BRANCH_NAME), latest)
TF_VAR_s3_tf_state_key := $(PROJECT_ID)/$(ENV)/s3/terraform.state
TF_VAR_security_groups_tf_state_key := $(PROJECT_ID)/$(ENV)/security-groups/terraform.state
TF_VAR_core_dos_db_sg := sg-0019e059390d78db7
TF_VAR_splunk_firehose_subscription := dos-cw-w-events-logs-firehose
TF_VAR_splunk_firehose_role := dos_cw_w_events_firehose_access_role

LAMBDA_VERSIONS_TO_RETAIN = 5
