import os
import streamlit as st
from streamlit_plotly_events import plotly_events
import subprocess
from src.common import *
from src.view import *
from src.fileupload import *
from src.result_files import *
from src.ini2dec import *
import threading
from src.captcha_ import *
from src.run_subprocess import *

params = page_setup()

# If run in hosted mode, show captcha as long as it has not been solved
if 'controllo' not in st.session_state or params["controllo"] == False:
    # Apply captcha by calling the captcha_control function
    captcha_control()        

### main content of page

# title of page
st.title("⚙️ Run Analysis")

######################## Take NuXL configurations ini read #################################
# Define the sections you want to extract
# will capture automaticaly if add new section as decoy_factor 
sections = [
    "fixed",
    "variable",
    "presets",
    "enzyme",
    "scoring",
    "variable_max_per_peptide",
    "length",
    "mass_tolerance", # will store in config dict both precursor_mass_tolerance_unit, and fragmant_mass_tolerance_unit
    "mass_tolerance_unit", # will store in config dict both precursor_mass_tolerance, and fragmant_mass_tolerance
    "min_size",
    "max_size",
    "missed_cleavages"
]

# current directory
current_dir = os.getcwd()
# take .ini config path
config_path = os.path.join(current_dir, 'assets', 'OpenMS_NuXL.ini')
# take NuXL config dictionary 
# (will give every section as 1 entry: 
# entry = {
        #"name": node_name,
        #"default": node_default,
        #"description": node_desc,
        #"restrictions": restrictions_list
        # })
NuXL_config=ini2dict(config_path, sections)

# make sure "selected-mzML-files" is in session state
if "selected-mzML-files" not in st.session_state:
    st.session_state["selected-mzML-files"] = params.get("selected-mzML-files", [])

# make sure "selected-fasta-files" is in session state
if "selected-fasta-files" not in st.session_state:
    st.session_state["selected-fasta-files"] = params.get("selected-fasta-files", [])

# make sure mzML example files in current session state
load_example_mzML_files()

# take mzML files from current session file
mzML_files_ = [f.name for f in Path(st.session_state.workspace, "mzML-files").iterdir()]

#delete_files(directory = Path(st.session_state.workspace, "mzML-files"), remove_files_end_with = '.raw.mzML')

# make sure fasta example files in current session state
load_example_fasta_files()

# take fasta files from current session file
fasta_files = [f.name for f in Path(st.session_state.workspace,"fasta-files").iterdir()]

# put Trypsin as first enzyme
if 'Trypsin/P' in NuXL_config['enzyme']['restrictions']:
    NuXL_config['enzyme']['restrictions'].remove('Trypsin/P')
    NuXL_config['enzyme']['restrictions'].insert(0, 'Trypsin/P')

with st.form("fasta-upload", clear_on_submit=False):

    # selected mzML file from mzML files list
    selected_mzML_file = st.selectbox(
        "choose mzML/raw file",
        [item for item in mzML_files_ if not item.endswith(".csv")]
        ,
        help="If file not here, please upload at File Upload"
    )

    # select fasta file from mzML files list
    selected_fasta_file = st.selectbox(
        "choose fasta file",
        [f.name for f in Path(st.session_state.workspace,
                            "fasta-files").iterdir()],
        help="If file not here, please upload at File Upload"
    )

    # take full path of mzML file
    if selected_mzML_file:
        mzML_file_path = str(Path(st.session_state.workspace, "mzML-files", selected_mzML_file))

    # take full path of fasta file
    if selected_fasta_file:
        database_file_path = str(Path(st.session_state.workspace, "fasta-files", selected_fasta_file))

    # take all variables settings from config dictionary/ take all user configuration
    cols=st.columns(2)
    with cols[0]:
        cols_=st.columns(2)
        with cols_[0]:
            Enzyme = st.selectbox('enzyme', NuXL_config['enzyme']['restrictions'], help=NuXL_config['enzyme']['description'])
        with cols_[1]:
            Missed_cleavages = str(st.number_input("missed cleavages",value=int(NuXL_config['missed_cleavages']['default']), help=NuXL_config['missed_cleavages']['description'] + " default: "+ NuXL_config['missed_cleavages']['default']))
            if int(Missed_cleavages) <= 0:
                st.error("Length must be a positive integer greater than 0")

    with cols[1]:
        cols_=st.columns(2)
        with cols_[0]:
            peptide_min = str(st.number_input('peptide min length', value=int(NuXL_config['min_size']['default']), help=NuXL_config['min_size']['description'] + " default: "+ NuXL_config['min_size']['default']))
            if int(peptide_min) < 1:
                    st.error("Length must be a positive integer greater than 0")

        with cols_[1]:
            peptide_max= str(st.number_input('peptide max length', value=int(NuXL_config['max_size']['default']), help=NuXL_config['max_size']['description'] + " default: "+ NuXL_config['max_size']['default']))
            if int(peptide_max) < 1:
                    st.error("Length must be a positive integer greater than 1")

    cols=st.columns(2)
    with cols[0]:
        cols_=st.columns(2)
        with cols_[0]:
            Precursor_MT = str(st.number_input("precursor mass tolerance",value=float(NuXL_config['precursor_mass_tolerance']['default']), help=NuXL_config['precursor_mass_tolerance']['description'] + " default: "+ NuXL_config['precursor_mass_tolerance']['default']))
            if float(Precursor_MT) <= 0:
                st.error("Precursor mass tolerance must be a positive integer")

        with cols_[1]:
            #Precursor_MT_unit= st.selectbox('precursor mass tolerance unit',NuXL_config['precursor_mass_tolerance_unit']['restrictions'], help=NuXL_config['precursor_mass_tolerance_unit']['description'] + " default: "+ NuXL_config['precursor_mass_tolerance_unit']['default'])
            Precursor_MT_unit = cols_[1].radio(
            "precursor mass tolerance unit",
            NuXL_config['precursor_mass_tolerance_unit']['restrictions'], 
            help=NuXL_config['precursor_mass_tolerance_unit']['description']  + " default: "+ NuXL_config['precursor_mass_tolerance_unit']['default'],
            key="Precursor_MT_unit"
            )

    with cols[1]:
        cols_=st.columns(2)
        with cols_[0]:
            Fragment_MT = str(st.number_input("fragment mass tolerance",value=float(NuXL_config['fragment_mass_tolerance']['default']), help=NuXL_config['fragment_mass_tolerance']['description'] + " default: "+ NuXL_config['fragment_mass_tolerance']['default']))
            if float(Fragment_MT) <= 0:
                st.error("Fragment mass tolerance must be a positive integer")

        with cols_[1]:
            #Fragment_MT_unit= st.selectbox('fragment mass tolerance unit', NuXL_config['precursor_mass_tolerance_unit']['restrictions'], help=NuXL_config['fragment_mass_tolerance_unit']['description'] + " default: "+ NuXL_config['fragment_mass_tolerance_unit']['default'])
            Fragment_MT_unit = cols_[1].radio(
            "fragment mass tolerance unit",
            NuXL_config['precursor_mass_tolerance_unit']['restrictions'], 
            help=NuXL_config['fragment_mass_tolerance_unit']['description']+ " default: "+ NuXL_config['fragment_mass_tolerance_unit']['default'],
            key="Fragment_MT_unit"
            )

    cols=st.columns(2)
    with cols[0]:
        preset = st.selectbox('select the suitable preset',NuXL_config['presets']['restrictions'], help=NuXL_config['presets']['description'] + " default: "+ NuXL_config['presets']['default'])
    with cols[1]:
        length = str(st.number_input("length of oligonucleotide",value=int(NuXL_config['length']['default']), help=NuXL_config['length']['description'] + " default: "+ NuXL_config['length']['default']))
        if int(length) <= -1:
            st.error("Length must be a positive integer.")

    cols=st.columns(2)
    with cols[0]:
        fixed_modification = st.multiselect('select fixed modifications:', NuXL_config['fixed']['restrictions'], help=NuXL_config['fixed']['description'] + " default: "+ NuXL_config['fixed']['default'])

    with cols[1]: 
        variable_modification = st.multiselect('select variable modifications:', NuXL_config['variable']['restrictions'], help=NuXL_config['variable']['description'] + " default: "+ NuXL_config['variable']['default'], default = "Oxidation (M)")
        
    cols=st.columns(2)
    with cols[0]:
        Variable_max_per_peptide  = str(st.number_input("variable modification max per peptide",value=int(NuXL_config['variable_max_per_peptide']['default']), help=NuXL_config['variable_max_per_peptide']['description'] + " default: "+ NuXL_config['variable_max_per_peptide']['default']))
        if int(Variable_max_per_peptide) <= -1:
            st.error("variable modification max per peptide must be a positive integer")

    with cols[1]:
        #scoring  = st.selectbox('select the scoring method',NuXL_config['scoring']['restrictions'], help=NuXL_config['scoring']['description'] + " default: "+ NuXL_config['scoring']['default'])
        scoring = cols[1].radio(
        "select the scoring method",
        [NuXL_config['scoring']['restrictions'][1], NuXL_config['scoring']['restrictions'][0]],
        help=NuXL_config['scoring']['description'] + " default: "+ NuXL_config['scoring']['default'],
        key="scoring"
        )
 
# out file path
result_dir: Path = Path(st.session_state.workspace, "result-files")

# create same output file path name as input file path
mzML_file_name = os.path.basename(mzML_file_path)
protocol_name = os.path.splitext(mzML_file_name)[0]
result_path = os.path.join(result_dir, protocol_name + ".idXML")

##################################### NuXL command (subprocess) ############################

# result dictionary to capture output of subprocess
result_dict = {}
result_dict["success"] = False
result_dict["log"] = " "

# create terminate flag from even function
terminate_flag = threading.Event()
terminate_flag.set()

# terminate subprocess by terminate flag
def terminate_subprocess():
    global terminate_flag
    terminate_flag.set()

# run analysis 
if cols[0].form_submit_button("Run-analysis", type="primary"):

    # To terminate subprocess and clear form
    if st.button("Terminate/Clear", key="terminate-button", type="secondary"):
        # terminate subprocess
        terminate_subprocess()
        st.warning("Process terminated. The analysis may not be complete.")

        # clear form
        st.rerun() 

    # with st.spinner("Running analysis... Please wait until analysis done 😑"): #without status/ just spinner button
    with st.status("Running analysis... Please wait until analysis done 😑"):

        if mzML_file_path.endswith(".raw.mzML"):
            st.warning(f"(.raw.mzML) not supported, please select (.raw) or (.mzML) format",  icon="ℹ️")
        
        else:
            # If session state is local
            if st.session_state.location == "local":
              
                OpenNuXL_exec = os.path.join(os.getcwd(),'openms-bin', 'OpenNuXL')
                perc_exec = os.path.join(os.getcwd(), 'openms-thirdparty', 'Percolator', 'percolator.exe') 
                thermo_exec_path = os.path.join(os.getcwd(), 'openms-thirdparty', 'ThermoRawFileParser', 'ThermoRawFileParser.exe')

                args = [OpenNuXL_exec, "-ThermoRaw_executable", thermo_exec_path, "-in", mzML_file_path, "-database", database_file_path, "-out", result_path, "-NuXL:presets", preset, 
                                "-NuXL:length", length, "-NuXL:scoring", scoring, "-precursor:mass_tolerance",  Precursor_MT, "-precursor:mass_tolerance_unit",  Precursor_MT_unit,
                                "-fragment:mass_tolerance",  Fragment_MT, "-fragment:mass_tolerance_unit",  Fragment_MT_unit,
                                "-peptide:min_size", peptide_min, "-peptide:max_size",peptide_max, "-peptide:missed_cleavages",Missed_cleavages, "-peptide:enzyme", Enzyme,
                                "-modifications:variable_max_per_peptide", Variable_max_per_peptide
                                ]

                args.extend(["-percolator_executable", perc_exec])

            # If session state is online/docker
            else:  

                thermo_exec_path = "/thirdparty/ThermoRawFileParser/ThermoRawFileParser.exe"
                # In docker it executable on path
                args = ["OpenNuXL", "-ThermoRaw_executable", thermo_exec_path, "-in", mzML_file_path, "-database", database_file_path, "-out", result_path, "-NuXL:presets", preset, 
                            "-NuXL:length", length, "-NuXL:scoring", scoring, "-precursor:mass_tolerance",  Precursor_MT, "-precursor:mass_tolerance_unit",  Precursor_MT_unit,
                            "-fragment:mass_tolerance",  Fragment_MT, "-fragment:mass_tolerance_unit",  Fragment_MT_unit,
                            "-peptide:min_size", peptide_min, "-peptide:max_size",peptide_max, "-peptide:missed_cleavages",Missed_cleavages, "-peptide:enzyme", Enzyme,
                            "-modifications:variable_max_per_peptide", Variable_max_per_peptide
                            ]

            # If variable modification provided
            if variable_modification: 
                args.extend(["-modifications:variable"])
                args.extend(variable_modification)

            # If fixed modification provided
            if fixed_modification: 
                args.extend(["-modifications:fixed"])
                args.extend(fixed_modification)
            
            # Add any additional variables needed for the subprocess (if any)
            variables = []  

            # want to see the command values and argues
            #message = f"Running '{' '.join(args)}'"
            #st.info(message)
            st.info(f"Analyzing {mzML_file_path}",  icon="ℹ️")

            # run subprocess command
            run_subprocess(args, variables, result_dict)

            #rename the file .raw.mzML --> .mzML
            rename_files(Path(st.session_state.workspace, "mzML-files"))
            
            # Use st.experimental_thread to run the subprocess asynchronously
            # terminate_flag = threading.Event()
            # thread = threading.Thread(target=run_subprocess, args=(args, variables, result_dict))
            # thread.start()
            # thread.join()

        delete_files(directory = Path(st.session_state.workspace, "mzML-files"), remove_files_end_with = '.raw.mzML')

    # if run_subprocess success (no need if not success because error will show/display in run_subprocess command)
    if result_dict["success"]:

        # add .mzML.ambigious_masses.csv in result directory 
        add_this_result_file(f"{protocol_name}.mzML.ambigious_masses.csv", Path(st.session_state.workspace, "mzML-files"))
        
        # remove .mzML.ambigious_masses.csv from mzML directory
        remove_this_mzML_file(f"{protocol_name}.mzML.ambigious_masses.csv")

        # Save the log to a text file in the result_dir
        log_file_path = result_dir / f"{protocol_name}_log.txt"
        with open(log_file_path, "w") as log_file:
            log_file.write(result_dict["log"])

        # all result files in result-dir
        All_files = [f.name for f in sorted(result_dir.iterdir())]

        # filtered out all current run file from all resul-dir files
        current_analysis_files = [s for s in All_files if protocol_name in s]

        # add list of files to dataframe
        df = pd.DataFrame({"output files ": current_analysis_files})

        # show table of all list files of current protocol
        show_table(df)

        # check if perc files availabe in some cases could not run percolator e-g if identification hits are so less
        perc_exec = any("_perc_" in string for string in current_analysis_files)

        # just show and download the identification_files of XLs PSMs/PRTs if perc_XLs available otherwise without the percolator identification file
        if perc_exec :
            identification_files = [string for string in current_analysis_files if "_perc_0.0100_XLs"  in string or "_perc_0.1000_XLs" in string or "_perc_1.0000_XLs" in string or "_perc_proteins" in string]
        else:
            identification_files = [string for string in current_analysis_files if "_XLs"  in string or "_proteins" in string]

        # then download link for identification file of above criteria 
        download_selected_result_files(identification_files, f":arrow_down: {protocol_name}_XL_identification_files")


save_params(params)