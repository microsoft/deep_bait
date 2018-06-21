from __future__ import print_function

import json
import logging
import os
import pprint
import time

import azure.mgmt.batchai as training
import azure.mgmt.batchai.models as models
import requests
from azure.common.credentials import ServicePrincipalCredentials
from azure.storage.file import FileService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

POLLING_INTERVAL_SEC = 5


def encode(value):
    if isinstance(value, type('str')):
        return value
    return value.encode('utf-8')


class Configuration(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @staticmethod
    def from_file(filename):
        if not os.path.exists(filename):
            raise ValueError('Cannot find configuration file "{0}"'.format(filename))

        with open(filename, 'r') as f:
            return Configuration(**json.load(f))

    @staticmethod
    def from_dict(conf_dict):
        return Configuration(**conf_dict)

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def __str__(self):
        return pprint.pformat(self.__dict__)


class OutputStreamer:
    """Helper class to stream (tail -f) job's output files."""

    def __init__(self, client, resource_group, job_name, output_directory_id,
                 file_name):
        self.client = client
        self.resource_group = resource_group
        self.job_name = job_name
        self.output_directory_id = output_directory_id
        self.file_name = file_name
        self.url = None
        self.downloaded = 0
        # if no output_directory_id or file_name specified, the tail call is
        # nope
        if self.output_directory_id is None or self.file_name is None:
            self.tail = lambda: None

    def tail(self):
        if not self.url:
            files = self.client.jobs.list_output_files(
                self.resource_group, self.job_name,
                models.JobsListOutputFilesOptions(
                    outputdirectoryid=self.output_directory_id))
            if not files:
                return
            else:
                for f in list(files):
                    if f.name == self.file_name:
                        self.url = f.download_url
        if self.url:
            r = requests.get(self.url, headers={
                'Range': 'bytes={0}-'.format(self.downloaded)})
            if int(r.status_code / 100) == 2:
                self.downloaded += len(r.content)
                print(r.content.decode(), end='')


# def client_from(configuration):
#     ''' Returns a Batch AI client based on config
#     '''
#     client = training.BatchAITrainingClient(
#         configuration.subscription_id,
#         configuration.api_version,
#         configuration.url)
#     # During private preview we need to setup x-ms-auth-cert manually
#     client._client.add_header("x-ms-auth-cert", configuration.access_key)
#     client.config.generate_client_request_id = True
#     return client


def client_from(configuration):
    client = training.BatchAIManagementClient(
			credentials = ServicePrincipalCredentials(client_id=configuration.client_id, secret=configuration.secret, token_uri=configuration.token),
			subscription_id = configuration.subscription_id)
    return client


def download_file(sas, destination):
    dir_name = os.path.dirname(destination)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    print('Downloading {0} ...'.format(sas), end='')
    r = requests.get(sas, stream=True)
    with open(destination, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    f.close()
    print('Done')


def print_job_status(job):
    failure_message = None
    exit_code = 'None'
    if job.execution_info is not None:
        exit_code = job.execution_info.exit_code
    if job.execution_state == models.ExecutionState.failed:
        for error in job.execution_info.errors:
            failure_message = \
                '\nErrorCode:{0}\nErrorMessage:{1}\n'. \
                format(error.code,
                       error.message)
            if error.details is not None:
                failure_message += 'Details:\n'
                for detail in error.details:
                    failure_message += '{0}:{1}\n'.format(detail.name,
                                                          detail.value)
    print('Job state: {0} ExitCode: {1}'.format(job.execution_state.name,
                                                exit_code))
    if failure_message:
        print('FailureDetails: {0}'.format(failure_message))


def print_cluster_status(cluster):
    print(
        'Cluster state: {0} Target: {1}; Allocated: {2}; Idle: {3}; '
        'Unusable: {4}; Running: {5}; Preparing: {6}; Leaving: {7}'.format(
            cluster.allocation_state,
            cluster.scale_settings.manual.target_node_count,
            cluster.current_node_count,
            cluster.node_state_counts.idle_node_count,
            cluster.node_state_counts.unusable_node_count,
            cluster.node_state_counts.running_node_count,
            cluster.node_state_counts.preparing_node_count,
			cluster.node_state_counts.leaving_node_count))
    if not cluster.errors:
        return
    for error in cluster.errors:
        print('Cluster error: {0}: {1}'.format(error.code, error.message))
        if error.details:
            print('Details:')
            for detail in error.details:
                print('{0}: {1}'.format(detail.name, detail.value))


def wait_for_cluster(config, resource_group, workspace, cluster_name, polling_interval=POLLING_INTERVAL_SEC):
    client = client_from(config)
    while True:
        try:
            cluster = client.clusters.get(resource_group, workspace, cluster_name)
            print_cluster_status(cluster)
            if (cluster.scale_settings.manual.target_node_count == cluster.current_node_count
                and cluster.node_state_counts.preparing_node_count == 0 and
                cluster.node_state_counts.idle_node_count > 0 or
                    cluster.errors):
                return cluster
        except:
            pass
        time.sleep(polling_interval)


def wait_for_job_completion(client, resource_group, workspace, experiment, job_name, cluster_name,
                            output_directory_id=None, file_name=None, polling_interval=POLLING_INTERVAL_SEC):
    """
    Waits for job completion and tails a file specified by output_directory_id
    and file_name.
    """
    # Wait for job to start running
    while True:
        cluster = client.clusters.get(resource_group, workspace, cluster_name)
        print_cluster_status(cluster)
        job = client.jobs.get(resource_group, workspace, experiment, job_name)
        print_job_status(job)
        if job.execution_state != models.ExecutionState.queued:
            break
        time.sleep(polling_interval)

    print('Waiting for job output to become available...')

    # Tail the output file and wait for job to complete
    streamer = OutputStreamer(client, resource_group, job_name,
                              output_directory_id, file_name)
    while True:
        streamer.tail()
        job = client.jobs.get(resource_group, job_name)
        if job.execution_state == models.ExecutionState.succeeded:
            break
        time.sleep(1)
    streamer.tail()
    print_job_status(job)


def upload_scripts(config, job_name, filenames):
    service = FileService(config.storage_account['name'],
                          config.storage_account['key'])
    if not service.exists(config.fileshare_name, directory_name=job_name):
        service.create_directory(config.fileshare_name, job_name, fail_on_exist=False)
    trasfer_file = lambda fname: service.create_file_from_path(config.fileshare_name, job_name, os.path.basename(fname), fname)
    for filename in filenames:
        trasfer_file(filename)


def create_job(config, cluster_id, workspace, experiment, job_name, image_name, command, number_of_vms=1):
    ''' Creates job
    '''
    input_directories = [
        models.InputDirectory(
            id='SCRIPT',
            path='$AZ_BATCHAI_MOUNT_ROOT/{0}/{1}'.format(config.fileshare_mount_point, job_name)),
        models.InputDirectory(
            id='DATASET',
            path='$AZ_BATCHAI_MOUNT_ROOT/{0}/{1}'.format(config.fileshare_mount_point, 'data'))]

    std_output_path_prefix = "$AZ_BATCHAI_MOUNT_ROOT/{0}".format(config.fileshare_mount_point)

    output_directories = [
        models.OutputDirectory(
            id='MODEL',
            path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(config.fileshare_mount_point),
            path_suffix="models"),
        models.OutputDirectory(
            id='NOTEBOOKS',
            path_prefix='$AZ_BATCHAI_MOUNT_ROOT/{0}'.format(config.fileshare_mount_point),
            path_suffix="notebooks")
    ]

    parameters = models.JobCreateParameters(
        location=config.location,
        cluster=models.ResourceId(id=cluster_id),
        node_count=number_of_vms,
        input_directories=input_directories,
        std_out_err_path_prefix=std_output_path_prefix,
        output_directories=output_directories,
        container_settings=models.ContainerSettings(image_source_registry=models.ImageSourceRegistry(image=image_name)),
        custom_toolkit_settings=models.CustomToolkitSettings(command_line=command))


    client = client_from(config)
    _ = client.jobs.create(config.group_name, workspace, experiment, job_name, parameters)


def wait_for_job(config, job_name):
    client = client_from(config)
    wait_for_job_completion(client, config.group_name, job_name, config.cluster_name, 'stdOuterr', 'stdout.txt')


def setup_cluster(config, workspace):
    client = client_from(config)
    container_setting_for = lambda img: models.ContainerSettings(image_source_registry=models.ImageSourceRegistry(image=img))
    container_settings = [container_setting_for(img) for img in config.image_names]

    volumes = create_volume(config.storage_account['name'],config.storage_account['key'], config.fileshare_name, config.fileshare_mount_point)
    _ = client.workspaces.create(config.group_name, workspace, config.location).result()

    parameters = cluster_parameters_for(config, container_settings, volumes)
    _ = client.clusters.create(config.group_name, workspace, config.cluster_name, parameters)


def write_json_to_file(json_dict, filename):
    """ Simple function to write JSON dictionaries to files
    """
    with open(filename, 'w') as outfile:
        json.dump(json_dict, outfile)


def create_volume(storage_name, storage_key, azure_file_share_name, azure_file_share):
    return models.MountVolumes(
        azure_file_shares=[
            models.AzureFileShareReference(
                account_name=storage_name,
                credentials=models.AzureStorageCredentialsInfo(account_key=storage_key),
                azure_file_url='https://{0}.file.core.windows.net/{1}'.format(storage_name,
                                                                              azure_file_share_name),
                relative_mount_path=azure_file_share)
        ]
    )


def cluster_parameters_for(config, container_settings, volumes):
    return models.ClusterCreateParameters(
        virtual_machine_configuration=models.VirtualMachineConfiguration(
            image_reference=models.ImageReference(offer='UbuntuServer',
                                                  publisher='Canonical',
                                                  sku='16.04-LTS',
                                                  version='16.04.201708151')),
        location=config.location,
        vm_size=config.vm_type,
        user_account_settings=models.UserAccountSettings(
            admin_user_name=config.admin_user['name'],
            admin_user_password=config.admin_user['password']),
        scale_settings=models.ScaleSettings(
            manual=models.ManualScaleSettings(target_node_count=config.node_count)
        ),
        node_setup=models.NodeSetup(
            mount_volumes=volumes
        )
    )

def jobs_list_for(client,  workspace, experiment, resource_group=None):
    jobs_generator = client.jobs.list_by_experiment(resource_group, workspace, experiment)
    return [job.as_dict() for job in jobs_generator]


def print_jobs_for( workspace, experiment, client, resource_group=None):
    pprint.pprint(jobs_list_for(client,  workspace, experiment, resource_group=resource_group))


def print_jobs_summary_for( workspace, experiment, client, resource_group=None):
    for job in jobs_list_for(client,  workspace, experiment, resource_group=resource_group):
        print('{}: status:{} | exit-code {}'.format(job['name'],
                                                     job['execution_state'],
                                                     job.get('execution_info', dict()).get('exit_code', None)))


def delete_all_jobs_for(resource_group, workspace, experiment, client):
    for job in jobs_list_for(client, workspace, experiment, resource_group=resource_group):
        logger.info('Deleting {}'.format(job['name']))
        client.jobs.delete(resource_group, workspace, experiment, job['name'])
