import shutil
from pathlib import Path
import streamlit as st

from src.common import reset_directory

def add_to_selected_mzML(filename: str):
    """
    Add the given filename to the list of selected mzML files.

    Args:
        filename (str): The filename to be added to the list of selected mzML files.

    Returns:
        None
    """
    # Check if file in params selected mzML files, if not add it
    if filename not in st.session_state["selected-mzML-files"]:
        st.session_state["selected-mzML-files"].append(filename)

@st.cache_data
def save_uploaded_mzML(uploaded_files: list[bytes]) -> None:
    """
    Saves uploaded mzML files to the mzML directory.

    Args:
        uploaded_files (List[bytes]): List of uploaded mzML files.

    Returns:
        None
    """
    # A list of files is required, since online allows only single upload, create a list
    if st.session_state.location == "online":
        uploaded_files = [uploaded_files]
    # If no files are uploaded, exit early
    for f in uploaded_files:
        if f is None:
            st.warning("Upload some files first.")
            return
        
    # Write files from buffer to workspace mzML directory, add to selected files
    mzML_dir: Path = Path(st.session_state.workspace, "mzML-files")
    for f in uploaded_files:
        if f.name not in [f.name for f in mzML_dir.iterdir()] and (f.name.endswith("mzML") or f.name.endswith("raw")):
            with open(Path(mzML_dir, f.name), "wb") as fh:
                fh.write(f.getbuffer())
        add_to_selected_mzML(Path(f.name).stem)
    st.success("Successfully added uploaded files!")


@st.cache_data
def copy_local_mzML_files_from_directory(local_mzML_directory: str) -> None:
    """
    Copies local mzML files from a specified directory to the mzML directory.

    Args:
        local_mzML_directory (str): Path to the directory containing the mzML files.

    Returns:
        None
    """
    
    # Check if local directory contains mzML files, if not exit early
    if not any(Path(local_mzML_directory).glob("*.mzML")):
        st.warning("No mzML files found in specified folder.")
        return
    
    # Copy all mzML files to workspace mzML directory, add to selected files
    files = Path(local_mzML_directory).glob("*.mzML")
    mzML_dir: Path = Path(st.session_state.workspace, "mzML-files")
    for f in files:
        if f.name not in mzML_dir.iterdir():
            shutil.copy(f, mzML_dir)
        add_to_selected_mzML(f.stem)
    st.success("Successfully added local files!")


def load_example_mzML_files() -> None:
    """
    Copies example mzML files to the mzML directory.

    Args:
        None

    Returns:
        None
    """
    # Copy files from example-data/mzML to workspace mzML directory, add to selected files
    mzML_dir: Path = Path(st.session_state.workspace, "mzML-files")
    for f in Path("example-data", "mzML").glob("*.mzML"):
        shutil.copy(f, mzML_dir)
        add_to_selected_mzML(f.stem)
    #st.success("Example mzML files loaded!")

def remove_selected_mzML_files(to_remove: list[str]) -> None:
    """
    Removes selected mzML files from the mzML directory.

    Args:
        to_remove (List[str]): List of mzML files to remove.

    Returns:
        None
    """
    mzML_dir: Path = Path(st.session_state.workspace, "mzML-files")

    # remove all given files from mzML workspace directory and selected files
    for f in to_remove:
        Path(mzML_dir, f).unlink()
        #st.code(st.session_state["selected-mzML-files"])
        #st.session_state["selected-mzML-files"].remove(f)
    st.success("Selected mzML files removed!")


def remove_all_mzML_files() -> None:
    """
    Removes all mzML files from the mzML directory.

    Args:
        None

    Returns:
        None
    """
    mzML_dir: Path = Path(st.session_state.workspace, "mzML-files")

    # reset (delete and re-create) mzML directory in workspace
    reset_directory(mzML_dir)
    # reset selected mzML list
    st.session_state["selected-mzML-files"] = []
    st.success("All mzML files removed!")

def remove_this_mzML_file(to_remove: str) -> None:
    """
    Remove mzML file (full file name with extension like Example_RNA_UV_XL.mzML.ambigious_masses.csv) from the mzML directory.

    Args:
        to_remove (str): mzML file name to remove.

    Returns:
        None
    """
    mzML_dir: Path = Path(st.session_state.workspace, "mzML-files")
    to_remove_path = Path(mzML_dir, to_remove)
    for x in mzML_dir.iterdir():
        if x == to_remove_path:
            to_remove_path.unlink()

##################### Fasta ########################################################

def add_to_selected_fasta(filename: str):
    """
    Add the given filename to the list of selected fasta files.

    Args:
        filename (str): The filename to be added to the list of selected fasta files.

    Returns:
        None
    """
    # Check if file in params selected fasta files, if not add it
    if filename not in st.session_state["selected-fasta-files"]:
        #st.write("")
        st.session_state["selected-fasta-files"].append(filename)


@st.cache_data
def save_uploaded_fasta(uploaded_files: list[bytes]) -> None:
    """
    Saves uploaded fasta files to the fasta directory.

    Args:
        uploaded_files (List[bytes]): List of uploaded fasta files.

    Returns:
        None
    """
    fasta_dir: Path = Path(st.session_state.workspace, "fasta-files")

    # A list of files is required, since online allows only single upload, create a list
    if st.session_state.location == "online":
        uploaded_files = [uploaded_files]

    # If no files are uploaded, exit early
    for f in uploaded_files:
        if f is None:
            st.warning("Upload some files first.")
            return
        
    # Write files from buffer to workspace fasta directory, add to selected files
    for f in uploaded_files:
        if f.name not in [f.name for f in fasta_dir.iterdir()] and f.name.endswith("fasta"):
            with open(Path(fasta_dir, f.name), "wb") as fh:
                fh.write(f.getbuffer())
        add_to_selected_fasta(Path(f.name).stem)
    st.success("Successfully added uploaded files!")

def load_example_fasta_files() -> None:
    """
    Copies example fasta files to the fasta directory.

    Args:
        None

    Returns:
        None
    """

    fasta_dir: Path = Path(st.session_state.workspace, "fasta-files")

    # Copy files from example-data/fasta to workspace fasta directory, add to selected files
    for f in Path("example-data", "fasta").glob("*.fasta"):
        shutil.copy(f, fasta_dir)
        add_to_selected_fasta(f.stem)
    #st.success("Example fasta files loaded!")

@st.cache_data
def copy_local_fasta_files_from_directory(local_fasta_directory: str) -> None:
    """
    Copies local fasta files from a specified directory to the fasta directory.

    Args:
        local_fasta_directory (str): Path to the directory containing the fasta files.

    Returns:
        None
    """
    fasta_dir: Path = Path(st.session_state.workspace, "fasta-files")

    # Check if local directory contains fasta files, if not exit early
    if not any(Path(local_fasta_directory).glob("*.fasta")):
        st.warning("No fasta files found in specified folder.")
        return
    # Copy all fasta files to workspace fasta directory, add to selected files
    files = Path(local_fasta_directory).glob("*.fasta")
    for f in files:
        if f.name not in fasta_dir.iterdir():
            shutil.copy(f, fasta_dir)
        add_to_selected_fasta(f.stem)
    st.success("Successfully added local files!")

def remove_selected_fasta_files(to_remove: list[str]) -> None:
    """
    Removes selected fasta files from the fasta directory.

    Args:
        to_remove (List[str]): List of fasta files to remove.

    Returns:
        None
    """
    fasta_dir: Path = Path(st.session_state.workspace, "fasta-files")

    # remove all given files from fasta workspace directory and selected files
    for f in to_remove:
        Path(fasta_dir, f+".fasta").unlink()
        st.session_state["selected-fasta-files"].remove(f)
    st.success("Selected fasta files removed!")


def remove_all_fasta_files() -> None:
    """
    Removes all fasta files from the fasta directory.

    Args:
        None

    Returns:
        None
    """
    fasta_dir: Path = Path(st.session_state.workspace, "fasta-files")

    # reset (delete and re-create) fasta directory in workspace
    reset_directory(fasta_dir)
    # reset selected fasta list
    st.session_state["selected-fasta-files"] = []
    st.success("All fasta files removed!")

import os
def rename_files(directory: str) -> None:
    """
    Renames files in the given directory by removing '.raw' from files ending with '.raw.mzML'.

    Args:
        directory (str): The path to the directory containing the files to be renamed.

    Returns:
        None
    """
    # Iterate over all files in the given directory
    for filename in os.listdir(directory):
        # Check if the file ends with .raw.mzML
        if filename.endswith('.raw.mzML'):
            # Construct the new file name by replacing .raw.mzML with .mzML
            new_filename = filename.replace('.raw.mzML', '.mzML')
            # Construct full file paths
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)
            # Rename the file
            os.rename(old_file, new_file)

    return None