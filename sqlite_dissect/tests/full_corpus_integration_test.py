import unittest
from os.path import abspath, join, dirname, realpath, exists, basename, isfile

from main import main
from sqlite_dissect.utilities import get_sqlite_files, DotDict


class FullCorpusIntegrationTest(unittest.TestCase):

    def setUp(self):
        # Get the full path to avoid any nested issues
        self.base_path = abspath(join(dirname(realpath(__file__)), '..', '..'))
        self.input_root = join(self.base_path, 'test_files', 'corpus', 'sqlite_forensic_corpus_v1.0')
        self.output_path = join(self.base_path, 'output')

    def test_files_do_exist(self):
        self.assertTrue(exists(self.input_root))
        self.assertTrue(exists(self.output_path))
        corpus = get_sqlite_files(self.input_root)
        self.assertGreaterEqual(len(corpus), 1)

    def test_corpus_e2e(self):
        corpus = get_sqlite_files(self.input_root)

        # Loop through the files in the corpus and ensure they don't crash the SQLite Dissect tool
        for sqlite_file in corpus:
            # Build the arguments for the testing
            args = {
                'log_level': 'debug',
                'export': ['text'],
                'directory': self.output_path,
                'sqlite_file': sqlite_file
            }
            # Convert the dictionary to a dot-accessible object for the main parsing
            args = DotDict(args)

            output_file = join(self.output_path, basename(sqlite_file) + '.txt')

            # Call the main argument
            main(args)

            # Ensure the case.json file exists
            self.assertTrue(exists(output_file))
            self.assertTrue(isfile(output_file))


if __name__ == '__main__':
    unittest.main()
