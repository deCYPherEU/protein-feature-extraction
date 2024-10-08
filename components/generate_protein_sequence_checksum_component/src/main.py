"""
The GenerateProteinSequenceChecksumComponent is a component
that takes in a dataframe and applies a checksum to the sequence column.
The checksum is then added as a new column to the dataframe.
"""
import logging

from Bio.SeqUtils.CheckSum import crc64
from fondant.component import PandasTransformComponent
import pandas as pd


logger = logging.getLogger(__name__)


class GenerateProteinSequenceChecksumComponent(PandasTransformComponent):
    """
    The GenerateProteinSequenceChecksumComponent is a component
    that takes in a dataframe and applies a checksum to the sequence column.
    The checksum is then added as a new column to the dataframe.
    """

    def __init__(self, *_):
        # pylint: disable=super-init-not-called
        pass

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:  # pylint: disable=no-self-use
        """Apply a CRC64 checksum to each sequence and store the result in a new column."""

        dataframe['sequence_checksum'] = dataframe['sequence'].apply(crc64)

        return dataframe
