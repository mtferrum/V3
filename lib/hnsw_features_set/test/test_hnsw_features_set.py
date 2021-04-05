import unittest
import os
import numpy as np
import time
from lib.hnsw_features_set import HNSWFeaturesSet


class TestHNSWSet(unittest.TestCase):
    def setUp(self):
        self.set = HNSWFeaturesSet("/tmp/foo.bin", 10, 2)

    def tearDown(self):
        try:
            os.remove("/tmp/foo.bin")
        except FileNotFoundError:
            pass
        try:
            os.remove("/foo/bar.bin")
        except FileNotFoundError:
            pass

    def test_file_not_created_error(self):
        with self.assertRaises(FileNotFoundError):
            HNSWFeaturesSet("/foo/bar.bin", 1, 1)

    def test_rebuild(self):
        time_before_modification = os.path.getmtime(self.set.output_path)
        time.sleep(1)
        self.set.rebuild(np.array([[1, 1]]), np.asarray([1, ]))
        assert(time_before_modification != os.path.getmtime(self.set.output_path))

    def test_wrong_dimensionality(self):
        with self.assertRaises(RuntimeError):
            self.set.rebuild(np.array([[1, 1, 1]]), np.asarray([1, ]))

    def test_string_in_vector(self):
        with self.assertRaises(ValueError):
            self.set.rebuild(np.array([["I can't be converted to float", 1]]), np.asarray([1, ]))

    def test_string_list_id(self):
        with self.assertRaises(ValueError):
            self.set.rebuild(np.array([[1, 1]]), np.asarray(["I can't be converted to int", ]))

    def test_unsized_list_ids(self):
        with self.assertRaises(TypeError):
            self.set.rebuild(np.array([[1, 1]]), 1)

    def test_unequal_param_lengths(self):
        with self.assertRaises(AssertionError):
            self.set.rebuild(np.array([[1, 1]]), [1, 2])

    def test_duplicate_list_ids(self):
        with self.assertRaises(AssertionError):
            self.set.rebuild(np.array([[1, 1], [2, 2]]), [1, 1])

if __name__ == "__main__":
    unittest.main()
