ORG_NAME = nhsd-exeter
PROGRAMME = uec
PROJECT_GROUP = uec/dos
PROJECT_GROUP_SHORT = uec-dos
PROJECT_NAME = tasks
PROJECT_NAME_SHORT = tasks
PROJECT_DISPLAY_NAME = DoS Housekeeping and Tasks
PROJECT_ID = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)

ROLE_PREFIX = DoS
PROJECT_TAG = $(PROJECT_NAME)
SERVICE_TAG = $(PROJECT_GROUP_SHORT)
SERVICE_TAG_COMMON = core-dos

PROJECT_TECH_STACK_LIST = python,terraform

DOCKER_REPOSITORIES =
SSL_DOMAINS_PROD =
DEPLOYMENT_SECRETS = $(PROJECT_ID)-$(PROFILE)/deployment
SLACK_SECRETS = $(PROJECT_ID)-$(PROFILE)/slack

# Build slack secrets
TF_VAR_sm_required = false

# Texas  VPC
TF_VAR_vpc_name = lk8s-$(AWS_ACCOUNT_NAME).texasplatform.uk

# Housekeeping bucket name
TF_VAR_housekeeping_bucket_name = $(SERVICE_PREFIX)-housekeeping-bucket

# Housekeeping iam role name
TF_VAR_housekeeping_role_name = ${SERVICE_PREFIX}-hk-role
