-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := nonprod
ENVIRONMENT := nonprod
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)
VULNERABILITY_LEVEL := CRITICAL,HIGH

# ==============================================================================
# Infrastructure variables

STACKS := secrets,s3,security-groups,iam-role
# TODO restore  referralroles - temp out to avoid cross-cutting other work
TASKS := filter,referralroles,symptomgroups,symptomdiscriminators,symptomdiscriminatorsynonyms,symptomgroupdiscriminators,ragreset,removeoldchanges,stt,servicetypes
ENVIRONMENT_LIST := ["test","test1","test2","test3","test4","fix","performance","regression","teamb","testtech","template"]
TF_VAR_environment_list := $(ENVIRONMENT_LIST)

TF_VAR_deployment_secrets := $(DEPLOYMENT_SECRETS)
TF_VAR_image_version := $(or $(BUILD_TAG), latest)
TF_VAR_s3_tf_state_key := $(PROJECT_ID)/$(ENV)/s3/terraform.state
TF_VAR_security_groups_tf_state_key := $(PROJECT_ID)/$(ENV)/security-groups/terraform.state
TF_VAR_splunk_firehose_subscription := dos-cw-w-events-logs-firehose
TF_VAR_splunk_firehose_role := dos_cw_w_events_firehose_access_role

LAMBDA_VERSIONS_TO_RETAIN = 5


# Adding Performance and Regression SG as the legacy SG [live-lk8s-nonprod-core-dos-db-rds-postgres-sg]
# with access to all DB is being deprecated
# As a result adding additional SG to the Lambda used in nonprod
TF_VAR_add_perf_security_group = true
TF_VAR_add_regression_security_group = true
TF_VAR_add_perf_egress = true
TF_VAR_add_regression_egress = true
TF_VAR_add_perf_ingress = true
TF_VAR_add_regression_ingress = true

TF_VAR_db_security_group_name = uec-core-dos-pipeline-datastore-hk-sg
TF_VAR_db_performance_security_group_name =  uec-core-dos-performance-datastore-hk-sg
TF_VAR_db_regression_security_group_name = uec-core-dos-regression-datastore-hk-sg
