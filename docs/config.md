# Configuration File

To download a configuration file template users just use `--get_config` parameter. Using a config file your code is lot more clean and concise.

```bash
# get config
nextflow run fmalmeida/bacannot --get_config
# run with config
nextflow run fmalmeida/bacannot -c [path-to-config]
```

Default configuration
---------------------

```groovy
/*

                                          Required / Default Parameters.
                                        This parameters must always be set

*/
params {

    /*

            DB DOWNLOAD WORKFLOW
    
     */

// Trigger database download and formatting workflow? --> will not run annotation
// Will download and format a database inside {output} parameter
  get_dbs      = false
  force_update = false

    /*

            ANNOTATION INPUTS

    */

// Input data mus be given inside a well-formated samplesheet.
// We provide a well-formated example at: https://github.com/fmalmeida/test_datasets/raw/main/bacannot_testing_samplesheets/samplesheet.yaml
//
// Please read the example samplesheet so you can understand how to properly fill it.
//
// It is also documented in the main manual: https://bacannot.readthedocs.io/en/latest/samplesheet
  input = null

// path to directory containing databases used by bacannot
// you can download databases with: 
// nextflow run fmalmeida/bacannot --get_dbs --output bacannot_dbs -profile <docker/conda/singularity>
  bacannot_db = null

    /*

            GENERAL PARAMETERS

     */

// Main output folder name. More than one bacannot annotation can be redirected
// to the same output parameter. It is good to keep related annotations together.
// A subdirectory with the filename will be created inside this directory.
  output = 'results'

// Number of minimum overlapping base pairs required for merging
// Negative values, such as -20, means the number of required overlapping bases for merging.
// Positive values, such as 5, means the maximum distance accepted between features for merging.
// By default (if Blank), this process is not executed. For execution the user needs to provide a value
  bedtools_merge_distance = null

          /*
           * Prokka optional parameters
           */
// Do not use PGAP (NCBI) database?
// PGAP is big and using it may have higher running times but better results
// To do not use it, set the following to true
  prokka_use_pgap = false

// Annotation mode: Archaea|Bacteria|Mitochondria|Viruses (default 'Bacteria')
  prokka_kingdom = null

// Translation table code. Must be set if the above is set.
// Example: params.prokka_genetic.code = 11
  prokka_genetic_code = null

// Use rnammer instead of Barrnap? False or True?
  prokka_use_rnammer = false

          /*
           * Resfinder species panel
           */

// Species panel to be used when annotating with Resfinder.
// It sets a default for all samples in the samplesheet.
// If a sample has a different value inside the samplesheet it will overwrite the value for that sample
// If blank it will not be executed.
// It must be identical (without the *) as written in their webservice https://cge.cbs.dtu.dk/services/ResFinder/.
// E.g. 'Escherichia coli'; 'Klebsiella' ...
  resfinder_species = null

          /*
           * Handling the execution of processes
           *
           * By default, all processes are executed. These
           * parameters tells wheter NOT to run a process.
           *
           * Which means: false will allow its execution
           * while true will create a barrier and skip a process.

*/
// (NOT RUN?) Plasmids annotation (controls PlasmidFinder execution)
  skip_plasmid_search = false

// (NOT RUN?) General Virulence annotation (controls VFDB and Victors scan)
  skip_virulence_search = false

// (NOT RUN?) Resistance annotation (controls AMRfinder and RGI)
  skip_resistance_search = false

// (NOT RUN?) ICE annotation (controls ICEberg annotation)
  skip_iceberg_search = false

// (NOT RUN?) prophage annotation (controls PHAST and Phigaro)
  skip_prophage_search = false

// (NOT RUN?) KO (KEGG Orthology) annotation
  skip_kofamscan = false

// (NOT RUN?) antiSMASH (secondary metabolite) annotation
  skip_antismash = false

          /*
           * Custom databases can be used to annotate additional genes in the genome.
           * It runs a BLAST alignment against the genome, therefore, the custom database
           * More than one custom database can be given separated by commas.
           * Gene headers must be properly formated as described in the
           * documentation: https://bacannot.readthedocs.io/en/latest/custom-db
           */
// Custom fastas (PROT / NUCL)
  custom_db    = null
// Custom annotation using list of NCBI protein accs
  ncbi_proteins = null

          /*
           * Annotation thresholds to be used when scanning specific databases and features
           * Select a combination of thresholds that is meaningful for your data. Some of
           * the databases are protein-only, others are nucleotide only. We cannnot control
           * that and the databases will be scanned either if blastp or blastn using these
           * thresholds described here.
           */

// Identity threshold for plasmid annotation
  plasmids_minid = 90

// Coverage threshold for plasmid annotation
  plasmids_mincov = 60

// Virulence genes identity threshold
  blast_virulence_minid = 90

// Virulence genes coverage threshold
  blast_virulence_mincov = 90

// AMR genes identity threshold
  blast_resistance_minid= 90

// AMR genes coverage threshold
  blast_resistance_mincov = 90

// MGEs (ICEs and Phages) identity threshold
  blast_MGEs_minid = 85

// MGEs (ICEs and Phages) coverage threshold
  blast_MGEs_mincov = 85

// User's custom database identity threshold
  blast_custom_minid = 65

// User's custom database coverage threshold
  blast_custom_mincov = 65

// Max resource options
// Defaults only, expecting to be overwritten
  max_memory                 = '20.GB'
  max_cpus                   = 16
  max_time                   = '40.h'

}
```