Common:

This directory will hold all of the common terraform files that are required by all of the stacks. Each file will need to be named with a prefix of 'c-' and these files will automatically be copied into every stack prior to the terraform commands being executed.
Once the terraform commands have been executed, these common files will be deleted from the stack directory.

The make targets in the build/automation/lib/terraform.mk file will perform the above operations.
