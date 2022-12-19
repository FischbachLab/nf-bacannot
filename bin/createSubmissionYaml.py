#!/usr/bin/env python3
"""
USAGE:
python3 createSubmissionYaml.py \
    -g s3://maf-users/Nathan_Johns/Scratch/ \
    -project UHGG_Annotation \
    -prefix 20221219-test-1 \
    -s test.yaml \
    -b

Whats happening:

- Genomes from "s3://maf-users/Nathan_Johns/Scratch/" folder are being uploaded to the s3_output_path/"fasta" folder.
- A test.yaml file is created, based on specs in the baccannot pipeline and uploaded to the s3_output_path folder.
- The script generates a recommended command that you should use to submit the job.

Output:
aws batch submit-job \
    --job-name nf-bacannot-20221219-test-1 \
    --job-queue priority-maf-pipelines \
    --job-definition nextflow-production \
    --container-overrides command=FischbachLab/nf-bacannot,\
"-profile","maf_bakta",\
"--input","s3://genomics-workflow-core/Results/Bacannot/UHGG_Annotation/20221219-test-1/inputs/test.yaml",\
"--output","s3://genomics-workflow-core/Results/Bacannot/UHGG_Annotation/20221219-test-1"
"""

from cloudpathlib import CloudPath, AnyPath

import argparse
from ruamel.yaml import YAML

RESULTS_S3_BASE_PATH = CloudPath("s3://genomics-workflow-core/Results/Bacannot")

parser = argparse.ArgumentParser(
    description="Create submission YAML file for bacannot pipeline"
)
parser.add_argument(
    "-g",
    "--genome-dir",
    type=str,
    required=True,
    help="Directory with all the genomes with extension '.fna'",
)
parser.add_argument(
    "-project",
    type=str,
    required=False,
    default="00_TEST",
    help=(
        """
    Name of the project that this analysis belongs to.
    This will become part of your output path.
    No spaces, please.
    """
    ),
)
parser.add_argument(
    "-prefix",
    type=str,
    required=False,
    default="00_test_prefix",
    help=(
        """
    Name of the subset of the data within this Project that this analysis belongs to.
    This will become part of your output path.
    No spaces, please.
    """
    ),
)
parser.add_argument(
    "-b",
    "--use-bakta",
    action="store_true",
    help="Use 'Bakta' to annotate the genomes.",
)
parser.add_argument(
    "-s",
    "--seedfile",
    type=str,
    required=False,
    help="Name of the seedfile for the pipeline. By default, it is a combination of <PROJECT> and <PREFIX>",
)

args = parser.parse_args()

yaml = YAML()
yaml.default_flow_style = False
yaml.sort_keys = False
yaml.indent(mapping=2, sequence=4, offset=2)

fasta_dir = AnyPath(args.genome_dir)
s3_output_dir = RESULTS_S3_BASE_PATH / args.project / args.prefix / "inputs"

samplesheet_yaml = (
    AnyPath(args.seedfile)
    if args.seedfile
    else AnyPath(f"{args.project}-{args.prefix}.yaml")
)

s3_fasta_dir = s3_output_dir / "fasta"
s3_yaml_path = s3_output_dir / samplesheet_yaml.name

yaml_dict = {"samplesheet": []}

# Upload genomes to S3
for fasta_file in fasta_dir.glob("*.fna"):
    s3path = s3_fasta_dir / fasta_file.name
    yaml_dict["samplesheet"].append(
        {"id": str(fasta_file.stem), "assembly": str(s3path)}
    )
    s3path.upload_from(fasta_file)

# Write YAML file to S3
with s3_yaml_path.open("w") as s3_yaml_file:
    yaml.dump(yaml_dict, s3_yaml_file)

# with open(samplesheet_yaml, "w") as s3_yaml_file:
#     yaml.dump(yaml_dict, s3_yaml_file)

launch_profile = "maf_bakta" if args.use_bakta else "maf"

print(
    f"""
Submission command:\n
aws batch submit-job \\
    --job-name nf-bacannot-{args.prefix} \\
    --job-queue priority-maf-pipelines \\
    --job-definition nextflow-production \\
    --container-overrides command=FischbachLab/nf-bacannot,\\
"-profile","{launch_profile}",\\
"--input","{s3_yaml_path}",\\
"--output","{s3_output_dir.parent}"
"""
)
