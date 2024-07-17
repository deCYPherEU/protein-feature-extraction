"""
The MSA Component will take in a dataframe with a column of
sequences and return a dataframe with the MSA sequences as a new column
"""
import logging
import shutil
import subprocess  # nosec
import pandas as pd
from fondant.component import PandasTransformComponent


logger = logging.getLogger(__name__)


class MSAComponent(PandasTransformComponent):
    """
    The MSA Component will take in a dataframe with a column of
    sequences and return a dataframe with the MSA sequences as a new column
    """

    def __init__(self, *_):
        # pylint: disable=super-init-not-called
        pass

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Perform MSA on the sequences in the dataframe and add the MSA sequences
        to the dataframe
        """

        msa_file_content = self.execute_clustalo_cmd(dataframe)
        dataframe = self.add_msa_sequences_to_dataframe(
            msa_file_content, dataframe)

        return dataframe

    def create_fasta_file(self, dataframe: pd.DataFrame) -> str:
        """Create a faste file from the dataframe"""

        #TODO: this should be stored in the run folder, and not in the root of .fondant
        # however unclear right now how the correct folder name can be used in the container
        # output_file = "/.fondant/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".fasta"
        output_file = "all_seq.fasta"

        with open(output_file, "w") as f:
            for _, row in dataframe.iterrows():  # pylint: disable=unused-variable
                f.write(f">{row['sequence_checksum']}\n{row['sequence']}\n")

        return output_file


    def execute_clustalo_cmd(self, dataframe: pd.DataFrame) -> str:  # pylint: disable=no-self-use
        """Run Clustalo on the input file and return the content of the msa file"""

        # need to make sure all sequences are there
        # input_file = "all_sequences.fasta"
        output_file = "/.fondant/msa.fasta"

        # # Validate file extensions
        # if not input_file.endswith('.fasta') or not output_file.endswith('.fasta'):
        #     raise ValueError(
        #         "Invalid file extensions. Only .fasta files are allowed.")

        # Create output file
        with open(output_file, "w") as f:
            f.write("")

        # Write sequences to input file
        # with open(input_file, "w") as f:
        #     for _, row in dataframe.iterrows():  # pylint: disable=unused-variable
        #         f.write(f">{row['sequence_checksum']}\n{row['sequence']}\n")

        input_file = self.create_fasta_file(dataframe)

        # Get the full path to the Clustalo executable
        clustalo_path = shutil.which('clustalo')
        if clustalo_path:
            subprocess.run([clustalo_path, '-t', 'Protein', '-i',  # nosec
                            input_file, '-o', output_file, '--force'], check=True)  # nosec
        else:
            raise RuntimeError(
                "Clustalo executable not found in system's PATH")

        # Get content of output file
        with open(output_file, "r") as f:
            content = f.read()

        return content

    def add_msa_sequences_to_dataframe(self,
                                    msa_file_content: str,
                                    dataframe: pd.DataFrame) -> pd.DataFrame:
        # pylint: disable=no-self-use
        """Read the MSA file and add the MSA sequences to the dataframe"""

        msa_dict = {}
        current_sequence = None
        current_msa_sequence = ""

        for line in msa_file_content.split('\n'):
            if line.startswith('>'):
                if current_sequence is not None:
                    msa_dict[current_sequence] = current_msa_sequence
                current_sequence = line[1:].strip()
                current_msa_sequence = ""
            else:
                current_msa_sequence += line.strip()

        if current_sequence is not None:
            msa_dict[current_sequence] = current_msa_sequence

        dataframe['msa_sequence'] = dataframe['sequence_checksum'].map(
            msa_dict)

        return dataframe
