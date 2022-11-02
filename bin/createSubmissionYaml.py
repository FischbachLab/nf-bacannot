#!/usr/bin/env python3
"""
USAGE:
python3 createSubmissionYaml.py \\
    renamed \\
    s3://genomics-workflow-core/Results/Bacannot/hCom2/20221102/inputs \\
    hCom2.yaml

Whats happening:

- Genomes from "renamed" folder are being uploaded to the s3path/"fasta" folder.
- A hCom2.yaml file is created, based on specs in the baccannot pipeline and uploaded to the s3path folder.
- The script generates a recommended command that you should use to submit the job.

Output:
aws batch submit-job \\
    --job-name nf-bacannot-hCom2 \\
    --job-queue priority-maf-pipelines \\
    --job-definition nextflow-production \\
    --container-overrides command=FischbachLab/nf-bacannot,\\
"-profile","maf",\\
"--input","s3://genomics-workflow-core/Results/Bacannot/hCom2/20221102/inputs/hCom2.yaml",\\
"--output","s3://genomics-workflow-core/Results/Bacannot/hCom2/20221102"
"""

import sys
from cloudpathlib import CloudPath, AnyPath

# import yaml
from ruamel.yaml import YAML
from pprint import pprint

yaml = YAML()
yaml.default_flow_style = False
yaml.sort_keys = False
yaml.indent(mapping=2, sequence=4, offset=2)

local_fasta_dir = AnyPath(sys.argv[1])
s3_output_dir = CloudPath(sys.argv[2])
samplesheet_yaml = AnyPath(sys.argv[3])

s3_fasta_dir = s3_output_dir / "fasta"
s3_yaml_path = s3_output_dir / samplesheet_yaml.name

yaml_dict = {"samplesheet": []}

# Upload genomes to S3
for local_fasta_file in local_fasta_dir.glob("*.fna"):
    s3path = s3_fasta_dir / local_fasta_file.name
    yaml_dict["samplesheet"].append(
        {"id": str(local_fasta_file.stem), "assembly": str(s3path)}
    )
    s3path.upload_from(local_fasta_file)

# Write YAML file to S3
with s3_yaml_path.open("w") as s3_yaml_file:
    yaml.dump(yaml_dict, s3_yaml_file)

# with open(samplesheet_yaml, "w") as s3_yaml_file:
#     yaml.dump(yaml_dict, s3_yaml_file)

print(
    f"""
Submission command:\n
aws batch submit-job \\
    --job-name nf-bacannot-{samplesheet_yaml.stem} \\
    --job-queue priority-maf-pipelines \\
    --job-definition nextflow-production \\
    --container-overrides command=FischbachLab/nf-bacannot,\\
"-profile","maf",\\
"--input","{s3_yaml_path}",\\
"--output","{s3_output_dir.parent}"
"""
)
