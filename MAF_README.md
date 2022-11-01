# nf-baccannot

## Usage

```bash
aws batch submit-job \
    --job-name nf-bacannot-test-4 \
    --job-queue priority-maf-pipelines \
    --job-definition nextflow-production \
    --container-overrides command=FischbachLab/nf-bacannot,\
"-profile","maf",\
"--input","s3://genomics-workflow-core/Results/Bacannot/00_TEST/inputs/Slackia-exigua-ATCC-700122-MAF-2.yaml",\
"--output","s3://genomics-workflow-core/Results/Bacannot/00_TEST/20221031"
```
