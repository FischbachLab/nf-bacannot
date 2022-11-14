# nf-bacannot

This README describes how to launch the `Bacannot` pipeline on the MAF AWS Infrastructure.

For information about the original pipeline and all the tools that are used by the analysis pipeline please refer to the [Bacannot README](../README.md) file.

## Table of contents

- [nf-bacannot](#nf-bacannot)
  - [Table of contents](#table-of-contents)
  - [Please Note](#please-note)
  - [Usage](#usage)
    - [Helper Scripts](#helper-scripts)
      - [`renameFastaHeaders.py`](#renamefastaheaderspy)
        - [Example](#example)
      - [`createSubmissionYaml.py`](#createsubmissionyamlpy)
        - [Example](#example-1)
  - [Exploring the results](#exploring-the-results)
    - [Download results](#download-results)
    - [Launch Interactive Data Browser](#launch-interactive-data-browser)
    - [Shutdown the Data Browser](#shutdown-the-data-browser)

## Please Note

- A Contig ID is defined as the sequence header before the first space, please make sure that each ID is unique within the fasta file.
- Make sure that each Contig ID is less than `37` characters (before the first space). This is a hard limit set by the `prokka` pipeline. You may use a very basic helper script [`renameFastaHeaders.py`](../bin/renameFastaHeaders.py) for this. [USAGE](#renamefastaheaderspy).
- For simple use cases of this pipeline, where you only have a genome that needs annotation, there is a helper script [`createSubmissionYaml.py`](../bin/createSubmissionYaml.py) that will accept a local folder of fasta files, an s3path and an output yaml file name. [USAGE](#createsubmissionyamlpy).
- The [`createSubmissionYaml.py`](../bin/createSubmissionYaml.py) script will also print a suggested pipeline submission command that you may use to launch the pipeline using the submission files that you've just created.

## Usage

```bash
aws batch submit-job \
    --job-name nf-bacannot-hCom2 \
    --job-queue priority-maf-pipelines \
    --job-definition nextflow-production \
    --container-overrides command=FischbachLab/nf-bacannot,\
"-profile","maf",\
"--input","s3://genomics-workflow-core/Results/Bacannot/hCom2/20221102/inputs/hCom2.yaml"
"--output","s3://genomics-workflow-core/Results/Bacannot/hCom2/20221102"
```

### Helper Scripts

#### `renameFastaHeaders.py`

```bash
python renameFastaHeaders.py <ORIGINAL_FASTA_FILE> <RENAMED_FASTA_FILE>
```

##### Example

```bash
python renameFastaHeaders.py fasta_folder/genome.fasta renamed_fasta_folder/genome.fasta
```

#### `createSubmissionYaml.py`

```bash
python createSubmissionYaml.py <FASTA_DIR> s3://genomics-workflow-core/Results/Bacannot/<PROJECT>/<PREFIX>/inputs <PROJECT>_<PREFIX>.yaml
```

##### Example

```bash
python createSubmissionYaml.py renamed_fasta_folder s3://genomics-workflow-core/Results/Bacannot/hCom2/20221102/inputs hCom2.yaml
```

## Exploring the results

This pipeline generates A LOT of data per genome. Each genome contains a directory structure described [here](https://bacannot.readthedocs.io/en/latest/outputs). The easiest way to explore this data interactively is by using `docker`.

Make sure you have `docker` installed. See instructions [here](https://docs.docker.com/get-docker/).

Once `docker` is installed and running, sync the genome directory that is of interest to you, by using the `aws s3 sync` command. The following commands will explain the process using the annotation outputs of the `Slackia-exigua-ATCC-700122-MAF-2` genome, present on S3 at `s3://genomics-workflow-core/Results/Bacannot/00_TEST/20221031/`.

### Download results

```bash
aws s3 sync s3://genomics-workflow-core/Results/Bacannot/00_TEST/20221031/Slackia-exigua-ATCC-700122-MAF-2/ Slackia-exigua-ATCC-700122-MAF-2
```

This command will download all the data into a local folder called `Slackia-exigua-ATCC-700122-MAF-2`.

### Launch Interactive Data Browser

```bash
cd Slackia-exigua-ATCC-700122-MAF-2
docker run -v $(pwd):/work -d --rm --platform linux/amd64 -p 3838:3838 -p 4567:4567 --name ServerBacannot fmalmeida/bacannot:server
```

If this is your first time running this viewer, you might see docker trying to download a lot of data. This is normal and can take some time depending on your internet speeds. Once complete, you're now ready to interact with your data. Simply open your favorite web browser and go to [`http://localhost:3838/`](http://localhost:3838/). Note the use of `http` and not `https`. Some browsers may automatically make this change. In case you are unable to seen your webpage copy and paste this in your web browser (rather that clicking on this link).

If you're using an EC2 instance, go to the AWS EC2 console by logging into your AWS account and Identify your instance and note the `public IP address` for your instance. Open your favorite web browser and go to `http://Public.IP.Address:3838/`. Note the use of `http` and not `https`. Some browsers may automatically make this change. In case you are unable to seen your webpage copy and paste this in your web browser (rather that clicking on this link).

Et voila! You can now explore your data!

### Shutdown the Data Browser

All great things must come to an end. Use the following command to shut down your docker daemon that will in turn kill the data explorer webpage.

```bash
docker rm -f ServerBacannot
```
