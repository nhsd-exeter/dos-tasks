-include $(VAR_DIR)/profile/nonprod.mk # To allow for docker build to work correct

# ==============================================================================
# Service variables

TASKS := filter,referralroles,symptomgroups,symptomdiscriminators,ragreset,removeoldchanges,servicetypes,stt
TASKS := filter,referralroles,symptomgroups,symptomdiscriminators,symptomdiscriminatorsynonyms,ragreset,removeoldchanges,servicetypes,stt
