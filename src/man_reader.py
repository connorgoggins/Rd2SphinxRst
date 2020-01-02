import glob
import os

from src.rd_reader import RDReader
from src.rst_builder import RSTBuilder
from src.toctree_reader import TocTreeReader

class ManReader:
    '''
    ManReader reads a folder containing R Markdown files.

    Usage:
        mr = ManReader(path_to_rd_files)
        for rst in mr.get_rst():
            rst.write_rst_file(path_to_save_rsts)


    Parameter:
    ----------
    filepath: (str)
        Filepath of the R markdown files
    '''
    def __init__(self, filepath):
        self.rd_files = self.read_files(filepath)

    def read_files(self, filepath):
        '''
        Helper function to read all the MD files in a directory
        '''
        rd_files = []
        for rd_file in glob.glob(os.path.join(filepath, "*.Rd")):
            rd_files.append(RDReader(rd_file))
        return rd_files

    def write_rst(self, output_path, toctree_dir, url=""):
        '''
        Convert RDfiles and JSON files into RST files
        
        Parameter:
        ---------
        output_path: str
            Location to save the RST files

        toctree_dir: str
            Input directory of the toctree JSON files

        url: str
            URL of the repository
        '''
        for toctree_file in glob.glob(os.path.join(toctree_dir, "*.json")):
            tt = TocTreeReader(toctree_file, self.rd_files)
            tt.write_rst_file(output_path)

        for rd_file in self.rd_files:
            rst = RSTBuilder(rd_file, url)
            rst.write_rst_file(output_path)
