-include $(VAR_DIR)/profile/nonprod.mk # To allow for docker build to work correct

# ==============================================================================
# Service variables

TASKS := filter,referralroles,symptomgroups,symptomdiscriminators,ragreset,removeoldchanges,servicetypes
TASKS := filter,referralroles,symptomgroups,symptomdiscriminators,servicetypes
TASKS := filter,referralroles,symptomgroups,symptomdiscriminators,ragreset,removeoldchanges,stt
