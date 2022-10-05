-include $(VAR_DIR)/profile/nonprod.mk # To allow for docker build to work correct

# ==============================================================================
# Service variables

TASKS := filter,integration,referralroles,symptomgroups,symptomdiscriminators,symptomdiscriminatorsynonyms,symptomgroupdiscriminators,ragreset,removeoldchanges,servicetypes,stt
