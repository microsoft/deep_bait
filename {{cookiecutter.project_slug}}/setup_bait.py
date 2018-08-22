''' Script that sets everything up and introduces helper functions into the namespace
'''

import logging
logging.basicConfig(level=logging.ERROR)
import os
from glob import iglob
from itertools import chain
from os import path
from pprint import pprint
import utilities as ut
import azure.mgmt.batchai.models as models

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NODE_COUNT = 10
CLUSTER_NAME = 'mync6'
IMAGE_NAMES = ["masalvar/cntk_bait",
               "masalvar/chainer_bait",
               "masalvar/mxnet_bait",
               "masalvar/keras_bait",
               "masalvar/caffe2_bait",
               "masalvar/pytorch_bait",
               "masalvar/tf_bait"]

LOGGER_URL="dbait.eastus.cloudapp.azure.com"

def encode(value):
    if isinstance(value, type('str')):
        return value
    return value.encode('utf-8')


def current_bait_config(node_count=NODE_COUNT, cluster_name=CLUSTER_NAME, image_names=IMAGE_NAMES):
    return {
        "subscription_id": os.getenv('SUBSCRIPTION_ID'),
        "client_id": os.getenv('APP_ID'),
        "secret": os.getenv('SERVICE_PRINCIPAL_PWD'),
        "tenant": os.getenv('TENANT'),
        "access_key": os.getenv('BAIT_AUTHENTICATION'),
        "token": 'https://login.microsoftonline.com/{0}/oauth2/token'.format(encode(os.getenv('TENANT'))),
        "location": "eastus",
        "url": "",
        "api_version": "2017-05-01",
        "storage_account": {
            "name": os.getenv('STORAGE_ACCOUNT_NAME'),
            "key": os.getenv('STORAGE_ACCOUNT_KEY'),
        },
        "admin_user": {
            "name": "demoUser",  # TODO: Add if else from env
            "password": "Dem0Pa$$w0rd"
        },
        "node_count": node_count,
        "cluster_name": cluster_name,
        "image_names": image_names,
        "fileshare_name": os.getenv('FILE_SHARE_NAME'),
        "group_name": os.getenv('GROUP_NAME'),
        "fileshare_mount_point": 'azurefileshare',
        "vm_type": "STANDARD_NC6"
    }


config = ut.Configuration.from_dict(current_bait_config())

####### Cluster Functions #######################

def current_client():
    """ Returns the current Batch AI client
    """
    return ut.client_from(config)


client = current_client()


def current_cluster(workspace):
    """ Returns the cluster for the current config
    """
    return client.clusters.get(config.group_name, workspace, config.cluster_name)


def print_status(workspace):
    """ Print the current cluster status
    """
    ut.print_cluster_status(cluster=current_cluster(workspace))


def delete_cluster(workspace):
    """ Delete cluster
    """
    return client.clusters.delete(config.group_name, workspace, config.cluster_name)

    
def print_cluster_list(workspace, resource_group=config.group_name):
    """ Print cluster info
    """
    pprint([cl.as_dict() for cl in client.clusters.list_by_workspace(resource_group, workspace)])

    
def setup_cluster(workspace):
    """ Sets up the Batch AI cluster
    """
    ut.setup_cluster(config, workspace)


def wait_for_cluster(workspace):
    """ Will wait until the cluster is provisioned
    """
    ut.wait_for_cluster(config, config.group_name, workspace, config.cluster_name)


####### Jobs Functions #######################

def _upload_job_scripts(job_name):
    files = chain.from_iterable([iglob(path.join('exec_src', '*.ipynb')),
                                 iglob(path.join('exec_src', '*.sh')),
                                 iglob(path.join('exec_src', '*.py'))])
    ut.upload_scripts(config, job_name, files)



def submit_cntk_job(workspace, experiment, job_name='run_cntk', epochs=5):
    """ Submit CNTK job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	source /cntk/activate-cntk && \
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py CNTK_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/CNTK_{}.ipynb --EPOCHS={} --LOGGER_URL={}"'\
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/cntk_bait', command)


def submit_chainer_job(workspace, experiment, job_name='run_chainer', epochs=5):
    """ Submit Chainer job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py Chainer_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Chainer_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/chainer_bait', command)


def submit_mxnet_job(workspace, experiment, job_name='run_mxnet', epochs=5):
    """ Submit MXNet job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py MXNet_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/MXNet_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/mxnet_bait', command)


def submit_gluon_job(workspace, experiment, job_name='run_gluon', epochs=5):
    """ Submit Gluon job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py Gluon_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Gluon_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/mxnet_bait', command)


def submit_keras_cntk_job(workspace, experiment, job_name='run_keras_cntk', epochs=5):
    """ Submit Keras with CNTK backend job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	printenv && \
	python -u nb_execute.py Keras_CNTK_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Keras_CNTK_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/keras_bait', command)


def submit_keras_tf_job(workspace, experiment, job_name='run_keras_tf', epochs=5):
    """ Submit Keras with TF backend job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py Keras_TF_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Keras_TF_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/keras_bait', command)


def submit_caffe2_job(workspace, experiment, job_name='run_caffe2', epochs=5):
    """ Submit Caffe2 job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py Caffe2_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Caffe2_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/caffe2_bait', command)


def submit_pytorch_job(workspace, experiment, job_name='run_pytorch', epochs=5):
    """ Submit Pytorch job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	df -h && \
	python -u nb_execute.py Pytorch_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Pytorch_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/pytorch_bait', command)


def submit_tf_job(workspace, experiment, job_name='run_tf', epochs=5):
    """ Submit Tensorflow job
    """
    logger.info('Submitting job {}'.format(job_name))
    _upload_job_scripts(job_name)

    command = 'bash -c "\
	cd $AZ_BATCHAI_INPUT_SCRIPT && \
	python -u nb_execute.py Tensorflow_CIFAR.ipynb $AZ_BATCHAI_OUTPUT_NOTEBOOKS/Tensorflow_{}.ipynb --EPOCHS={} --LOGGER_URL={}"' \
        .format(job_name, epochs, LOGGER_URL)
    ut.create_job(config, current_cluster(workspace).id, workspace, experiment, job_name, 'masalvar/tf_bait', command)


def wait_for_job(workspace, experiment, job_name):
    """ Wait for the job to finish
    """
    ut.wait_for_job(config, workspace, experiment, job_name)


def delete_job(workspace, experiment, job_name):
    """ Deletes the job
    """
    logger.info('Deleting job {}'.format(job_name))
    client.jobs.delete(config.group_name, workspace, experiment, job_name)


def list_output_files(workspace, experiment, job_name, output_id):
    """ List the files for the specified job and output_id

   Parameters
   ----------
   job_name:  [str] The name of the job  e.g run_cntk, run_pytorch
   output_id: [str] The id of the output you want to download the files from e.g stdOuterr, notebooks
   """

    pprint(client.jobs.list_output_files(config.group_name, workspace, experiment, job_name, models.file_list_options.FileListOptions(output_id)).as_dict())


def download_files(workspace, experiment, job_name, output_id, output_folder=None):
    """ Downloads the files from the output of the job locally

    Parameters
    ----------
    job_name:  [str] The name of the job  e.g run_cntk, run_pytorch
    output_id: [str] The id of the output you want to download the files from e.g stdOuterr, notebooks
    """
    if output_folder:
        logger.info('Downloading files to {}'.format(output_folder))

    files = client.jobs.list_output_files(config.group_name, workspace, experiment, job_name, models.JobsListOutputFilesOptions(outputdirectoryid=output_id))
    for file in files:
        logger.info('Downloading {}'.format(file.name))
        file_name = path.join(output_folder, file.name) if output_folder else file.name
        ut.download_file(file.download_url, file_name)
    print("All files Downloaded")


def print_job_status(workspace, experiment, job_name):
    """ Prints the job status
    """
    job = client.job.get(config.group_name, workspace, experiment,job_name)
    ut.print_job_status(job)


def create_workspace(workspace):
    _ = client.workspaces.create(config.group_name, workspace, config.location).result()

def delete_workspace(workspace):
    _ = client.workspaces.delete(config.group_name, workspace).result()

def create_experiment(workspace, experiment):
    _ = client.experiments.create(config.group_name, workspace, experiment).result()

def delete_experiment(workspace, experiment):
    _ = client.experiments.delete(config.group_name, workspace, experiment).result()


def submit_all(workspace, experiment, epochs=5):
    """ Submits all jobs
    """
    jobs = (submit_cntk_job,
            submit_chainer_job,
            submit_mxnet_job,
            submit_keras_cntk_job,
            submit_keras_tf_job,
            submit_caffe2_job,
            submit_pytorch_job,
            submit_tf_job,
            submit_gluon_job)

    for job in jobs:
        job(workspace, experiment, epochs=epochs)


def delete_all_jobs( workspace, experiment):
    """ Deletes all jobs sent to the cluster
    """
    ut.delete_all_jobs_for(config.group_name,  workspace, experiment, client)


def print_jobs( workspace, experiment):
    """ Print information for all jobs
    """
    ut.print_jobs_for( workspace, experiment, client, resource_group=config.group_name)


def print_jobs_summary(workspace, experiment):
    """ Prints a summary of current jobs submitted to the cluster
    """
    ut.print_jobs_summary_for(workspace, experiment,client, resource_group=config.group_name)