#!/bin/bash -x

# update the date to today date. Format: YYYYMMDD
DATESTAMP=20221028

aws batch submit-job \
    --job-name nf-bacannot-getdbs \
    --job-queue priority-maf-pipelines \
    --job-definition nextflow-production \
    --container-overrides command=FischbachLab/nf-bacannot,\
"-profile","maf","docker",\
"--get_dbs",\
"--output","s3://genomics-workflow-core/Results/Bacannot/databases/${DATESTAMP}"

# Once this job has finished. Sync the `s3://genomics-workflow-core/Results/Bacannot/databases/${DATESTAMP}` path
# with the EFS mount path `/mnt/efs/databases/bacannot_dbs/${DATESTAMP}`.