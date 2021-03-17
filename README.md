# Executing from CLI

## Quickstart

`az ml folder attach -w WORKSPACE_NAME -g RESOURCE_GROUP_NAME`
`az ml run submit-script --async -c RunConfigurationFileFoundIn.azrumlFolder -e EXPERIMENT_NAME`

## Notes

* Install the CLI: https://docs.microsoft.com/en-us/azure/machine-learning/reference-azure-machine-learning-cli
* You'll need Contributor level access to execute experiments
* After running `az ml folder attach ...` you'll modify or create a Run Configuration file found in the .azureml folder
   * For running a single script, it's important that you update the script section the run configuration.


## References
* az ml run Documenation: https://docs.microsoft.com/en-us/cli/azure/ext/azure-cli-ml/ml/run?view=azure-cli-latest
* Overview of AML Pipeline Endpoints: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-machine-learning-pipelines
