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
import pandas as pd

RESULTS_S3_BASE_PATH = CloudPath("s3://genomics-workflow-core/Results/Bacannot")


def usage():
    parser = argparse.ArgumentParser(
        description="Create submission YAML file for bacannot pipeline"
    )
    parser.add_argument(
        "-g",
        "--genome-dir",
        type=str,
        required=False,
        help="Directory with all the genomes with extension 'fasta'",
    )
    parser.add_argument(
        "-t",
        "--genome-table",
        type=str,
        required=False,
        help="Command separated file with genome names and their corresponding s3 or local file paths, columns: genome_name, genome_path",
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
    parser.add_argument(
        "-e",
        "--extension",
        default="fasta",
        type=str,
        required=False,
        help="Extension for the genome files. Default is 'fasta'",
    )
    parser.add_argument(
        "--copy-genomes",
        default=False,
        action="store_true",
        required=False,
        help="Should input genomes be copied to the output path?",
    )
    return parser.parse_args()


def yaml_from_dir(args):
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
    for fasta_file in fasta_dir.glob(f"*.{args.extension}"):
        s3path = fasta_file
        # If genome is not already on S3, upload it and update the S3path
        if (not isinstance(s3path, CloudPath)) or args.copy_genomes:
            s3path = s3_fasta_dir / fasta_file.name
            s3path.upload_from(fasta_file)

        yaml_dict["samplesheet"].append(
            {"id": str(s3path.stem), "assembly": str(s3path)}
        )
    return s3_output_dir, s3_yaml_path, yaml_dict


def yaml_from_table(args):
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
    genome_table = pd.read_csv(
        args.genome_table, header=0, names=["genome_name", "genome_path"]
    )
    for row in genome_table.itertuples(index=False):
        s3path = AnyPath(row.genome_path)
        # If genome is not already on S3, upload it and update the S3path
        if (not isinstance(s3path, CloudPath)) or args.copy_genomes:
            s3path = s3_fasta_dir / row.genome_name
            s3path.upload_from(row.genome_path)

        yaml_dict["samplesheet"].append(
            {"id": str(row.genome_name), "assembly": str(s3path)}
        )
    return s3_output_dir, s3_yaml_path, yaml_dict


def main():
    args = usage()
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.sort_keys = False
    yaml.indent(mapping=2, sequence=4, offset=2)

    # assert either `genome_dir` or `genome_table` is provided
    if not (args.genome_dir or args.genome_table):
        raise ValueError(
            "Either `--genome-dir` or `--genome-table` must be provided. See `-h` for help."
        )

    # assert that `genome_dir` and `genome_table` are not both provided
    if args.genome_dir and args.genome_table:
        raise ValueError(
            "Only one of `--genome-dir` or `--genome-table` must be provided. See `-h` for help."
        )

    # assert that `genome_dir` or `genome_table` exists
    if args.genome_dir and not AnyPath(args.genome_dir).exists():
        raise ValueError(
            f"Provided `--genome-dir` does not exist: {args.genome_dir}. See `-h` for help."
        )
    if args.genome_table and not AnyPath(args.genome_table).exists():
        raise ValueError(
            f"Provided `--genome-table` does not exist: {args.genome_table}. See `-h` for help."
        )

    if args.genome_table:
        s3_output_dir, s3_yaml_path, yaml_dict = yaml_from_table(args)
    elif args.genome_dir:
        s3_output_dir, s3_yaml_path, yaml_dict = yaml_from_dir(args)

    # Write YAML file to S3
    with s3_yaml_path.open("w") as s3_yaml_file:
        yaml.dump(yaml_dict, s3_yaml_file)

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


if __name__ == "__main__":
    main()
