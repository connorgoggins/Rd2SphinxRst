import argparse

from src.man_reader import ManReader
from src.toctree_builder import TocTreeBuilder

# python Rd2SphinxRst.py ~/Desktop/mxnet/man/ ~/Desktop/mxnet/toctree ~/Desktop/mxnet/doc2/ --url http://github.com/apache/incubator-mxnet/blob/master/

def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert R Markdown to Sphinx compatible RST files.')
    parser.add_argument('man_dir', type=str,
                        help='Directory of the R Markdown files')
    parser.add_argument('toctree_dir', type=str,
                        help='Directory of the Toctree files')
    parser.add_argument('output_dir', type=str,
                        help='Directory to put the RST files')
    parser.add_argument('--url', type=str,
                        help="Base URL of the repository")
    return parser.parse_args()

def run():
    args = parse_args()
    mr = ManReader(args.man_dir)
    tb = TocTreeBuilder(args.man_dir)
    tb.write_tt(args.toctree_dir)
    mr.write_rst(args.output_dir, args.toctree_dir, url=args.url)

if __name__ == "__main__":
    run()
