-include $(VAR_DIR)/platform-texas/v1/account-live-k8s-prod.mk

# ==============================================================================
# Service variables

PROJECT_IMAGE_TAG :=
ENV := put
SERVICE_PREFIX := $(PROJECT_ID)-$(ENV)
AWS_LAMBDA_ECR = $(or $(AWS_ACCOUNT_ID), 000000000000).dkr.ecr.$(AWS_DEFAULT_REGION).amazonaws.com

# ==============================================================================
# Infrastructure variables

STACKS := s3
ENVIRONMENT_LIST := ["uat1","uat2","uat3","uat4","ut"]
