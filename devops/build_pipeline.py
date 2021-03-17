import argparse
from datetime import datetime
import os

from azureml.core import Datastore, RunConfiguration, Workspace, Run
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.exceptions import ComputeTargetException
from azureml.pipeline.core import Pipeline, PipelineData, PipelineEndpoint, PipelineParameter
from azureml.pipeline.steps import PythonScriptStep


if __name__ == "__main__":
    """
    Build the pipeline that trains, validates, and conditionally registers
    the model (upon successful validation).

    Expects a service principal and other parameters for AML and Databricks
    workspaces, along with the intendend training and validation sets.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--pipeline-name", 
        help="The name of the pipeline to be built or updated.")
    parser.add_argument("-s", "--datastore-name", 
        help="The name of the pipeline to be built or updated.")
    parser.add_argument("-d", "--description", 
        help="The description of the pipeline to be built or updated.")

    args = parser.parse_args()

    # TODO: Make this more dynamic
    pipeline_name = args.pipeline_name
    datastore_name = args.datastore_name
    description = args.description
    compute_name = os.environ.get("DBR_COMPUTE_NAME")
    
    # Authenticate to AML Workspace
    sp = ServicePrincipalAuthentication(
            tenant_id=os.environ.get("TENANT_ID"),
            service_principal_id=os.environ.get("CLIENT_ID"),
            service_principal_password=os.environ.get("CLIENT_SECRET")
    ) 

    print("Connecting to AML Workspace")
    ws = Workspace.get(
            name=os.environ.get("AML_WORKSPACE_NAME"),
            subscription_id=os.environ.get("AML_SUBSCRIPTION_ID"),
            auth=sp
    )
    ws.write_config()

    # Get Compute Target
    print("Gathering Compute Target")
    try:
        compute_object = ComputeTarget(
            workspace=ws, name=compute_name)
        print('Compute target already exists')
    except ComputeTargetException:
        print('compute not found')
        print('compute_name {}'.format(compute_name))
        
        raise Exception("Please create the ML compute cluster before running")
        
    # Get Datastore
    
    print("Creating Pipeline Steps")
    # Create Pipeline Steps
    # Consider including a RunConfiguration as well
    # https://docs.microsoft.com/en-us/python/api/azureml-core/azureml.core.runconfig.runconfiguration?view=azure-ml-py
    train_score = PythonScriptStep (
        script_name = "hello.py",
        name = "Friendly Name of this Step",
        compute_target = compute_object
        )


    # Create the pipeline and publish it
    current_date_time = datetime.strftime(datetime.now(), r'%Y%m%d%H%M')
    pipe = Pipeline(
        ws,
        steps = [train_score]
    )
    print("Publishing Pipelines")
    current_active_pipe_name = pipeline_name+current_date_time
    published_pipe = pipe.publish(current_active_pipe_name)

    print("New Published Pipeline: {}".format(str(published_pipe)))

    try:
        pipeline_endpoint = PipelineEndpoint.get(workspace=ws, name=pipeline_name)
        pipeline_endpoint.add_default(published_pipe)
        # Disable older pipelines to keep only one active in the endpoint
        all_active_sub_pipes = pipeline_endpoint.list_pipelines()
        for active_pipe in all_active_sub_pipes:
            if active_pipe.name == current_active_pipe_name:
                continue
            print(f"INFO: Disabling child pipeline '{active_pipe.name}'")
            active_pipe.disable()

        print("Successfully Added to existing pipeline")
        
    except Exception:
        pipeline_endpoint = PipelineEndpoint.publish(
            workspace=ws,
            name=pipeline_name,
            pipeline=published_pipe,
            description=description
        )
        print("Successfully created a new pipeline endpoint.")

    # NOTE: AZ ML CLI currently doesn't support caling the pipeline endpoint via CLI
    print(f"Completed pipeline build and deployment. ID: {published_pipe.id}")

