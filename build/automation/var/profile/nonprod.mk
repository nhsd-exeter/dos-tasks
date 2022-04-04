-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-nonprod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := nonprod
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)
AWS_LAMBDA_ECR = $(or $(AWS_ACCOUNT_ID), 000000000000).dkr.ecr.$(AWS_DEFAULT_REGION).amazonaws.com

# ==============================================================================
# Infrastructure variables

STACKS := s3
ENVIRONMENT_LIST := ["test","test1","test2","test3","test4","fix","performance","regression"]
