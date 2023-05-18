from cloudpathlib import AnyPath
import argparse
from ruamel.yaml import YAML
import logging


def usage():
    parser = argparse.ArgumentParser(
        description="Create submission YAML file for bacannot pipeline"
    )
    parser.add_argument(
        "-p",
        "--project_path",
        type=str,
        required=True,
        help="Directory with the results of the project the nf-bacannot run. Usually in the format: 's3://genomics-workflow-core/Results/Bacannot/<PROJECT>/<PREFIX>'",
    )
    parser.add_argument(
        "-s",
        "--seedfile",
        type=str,
        required=True,
        help="local or S3 Path to the YAML seedfile for the pipeline.",
    )
    parser.add_argument(
        "-f",
        "--overwrite",
        action="store_true",
        help="Overwrite the existing GFF files in the aggregate folder.",
    )
    return parser.parse_args()


def get_sample_names(yaml_seedfile):
    # read the yaml file
    yaml = YAML()
    yaml.preserve_quotes = True
    with yaml_seedfile.open("r") as f:
        seedfile = yaml.load(f)

    return {d["id"] for d in seedfile["samplesheet"]}


def copy_gffs(base_path: AnyPath, yaml_seedfile: str, overwrite: bool = False):
    assert base_path.exists(), f"{base_path} does not exist"

    output_folder = base_path / "00_aggregated_results" / "GFFs"
    output_folder.mkdir(parents=True, exist_ok=True)

    files_copied = 0
    missing_files = 0
    for sample in get_sample_names(yaml_seedfile):
        gff_path = AnyPath(f"{base_path}/{sample}/gffs/{sample}.gff")
        if not gff_path.exists():
            logging.warning(f"[{sample}] {gff_path} does not exist")
            missing_files += 1
            continue

        new_gff_path = output_folder / f"{sample}.gff"
        if (not new_gff_path.exists()) or overwrite:
            logging.debug(f"[{sample}] Copying {gff_path} to {new_gff_path}")
            gff_path.copy(new_gff_path, force_overwrite_to_cloud=overwrite)
            files_copied += 1

    logging.info("Finished copying GFF files.")
    logging.info(f"{missing_files} files were not found.")
    logging.info(f"Copied {files_copied} files to {output_folder}.")


def main():
    args = usage()
    base_path = AnyPath(args.project_path)
    yaml_seedfile = AnyPath(args.seedfile)
    overwrite = args.overwrite

    copy_gffs(base_path, yaml_seedfile, overwrite)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
