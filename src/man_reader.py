import glob
import os

from rd_reader import RDReader
from rst_builder import RSTBuilder

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
            print("RD-file {}".format(rd_file))
            rd_files.append(RDReader(rd_file))
        return rd_files

    def get_rst(self):
        '''
        Create a list of RSTBuilder objects
        '''
        rsts = []
        for rd_file in self.rd_files:
            rst = RSTBuilder(rd_file)
            rsts.append(rst)
        return rsts
