-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := put
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)

# ==============================================================================
# Infrastructure variables

STACKS := secrets,s3,security-groups
TASKS := filter,referralroles,symptomgroups,symptomdiscriminators
ENVIRONMENT_LIST := ["uat1","uat2","uat3","uat4","ut"]
TF_VAR_environment_list := $(ENVIRONMENT_LIST)

TF_VAR_deployment_secrets := $(DEPLOYMENT_SECRETS)
TF_VAR_image_version := $(or $(BUILD_TAG), latest)
TF_VAR_s3_tf_state_key := $(PROJECT_ID)/$(ENV)/s3/terraform.state
TF_VAR_security_groups_tf_state_key := $(PROJECT_ID)/$(ENV)/security-groups/terraform.state
TF_VAR_core_dos_db_sg := sg-03f2a9489cd60bf63
TF_VAR_splunk_firehose_subscription := dos-np-cw-w-events-logs-firehose
TF_VAR_splunk_firehose_role := dos-np_cw_w_events_firehose_access_role

LAMBDA_VERSIONS_TO_RETAIN = 5
