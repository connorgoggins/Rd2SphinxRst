import json
import textwrap
import os

class TocTreeBuilder:
    '''
    TocTreeBuilder generates a JSON file describing the toctree using the man/
    directory contents.
    
    Parameters:
    -----------
    man_dir: str
        Filepath of the R markdown files

    '''
    def __init__(self, man_dir):
        if os.path.isdir(man_dir):
            self.rd_filenames = []
            for entry in os.listdir(man_dir):
                if entry[-3:] == ".Rd":
                    self.rd_filenames.append(entry[:-3])
            self.get_tt()
        else:
            raise Exception("The provided path \"%s\" does not exist." % man_dir)

    def get_tt(self):
        '''
        Function to build the TOCTree dictionary.
        '''
        self.tt = {
                    "title": "R API",
                    "identifier": "r_api_docs",
                    "sections": [
                        {
                            "title": "R topics documented",
                            "type": "General-sub",
                            "subsection": [
                                {
                                    "title": "Functions",
                                    "type": "General",
                                    "print_api": True,
                                    "functions": self.rd_filenames,
                                    "toctree_properties": ":maxdepth: 2"
                                }
                            ]
                        }
                    ]
                  }

    def write_tt(self, toctree_dir):
        '''
        Function to write the TOCTree dictionary into a JSON file in storage.
        '''
        if os.path.isdir(toctree_dir):
            if toctree_dir[-1] != "/":
                toctree_dir += "/"
            with open(toctree_dir + 'tt.json', 'w') as fp:
                json.dump(self.tt, fp)
        else:
            raise Exception("The provided path \"%s\" does not exist." % toctree_dir)
