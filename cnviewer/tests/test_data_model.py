'''
Created on Dec 21, 2016

@author: lubo
'''
import numpy as np
from utils.model import DataModel
# import pytest


def test_data_model_create():

    model = DataModel('tests/data/cnviewer_data_example_00.zip')
    assert model is not None


def test_data_model_make():
    model = DataModel('tests/data/cnviewer_data_example_00.zip')
    model.make()


def test_data_model_make_01():
    model = DataModel('tests/data/cnviewer_data_example_01.zip')
    assert model is not None
    # model.make()


def test_make_pinmat():
    model = DataModel('tests/data/cnviewer_data_example_00.zip')
    assert model is not None

    model.make_linkage()
    model.make_dendrogram()
    model.make_pinmat()

#     expected = np.loadtxt('tests/data/pin_data_single.csv.gz',
#                           delimiter='\t')
#     assert expected is not None
#     print(expected.shape)
#     print(model.seg_data.shape)
#
#     count = 0
#     for i in xrange(model.bins):
#         for j in xrange(model.samples):
#             expected_val = expected[i, model.direct_lookup[j]]
#             if model.pins[i, j] != expected_val:
#                 label1 = model.column_labels[j]
#                 label2 = model.pinmat_df.columns[j]
#                 print(i, j, model.pins[i, j], expected_val, label1, label2)
#                 count += 1
#                 if count > 100:
#                     break
#         if count > 100:
#             break
#     print("total differences: {}".format(count))


#     assert model.pins[0, 72] == 1
#     assert model.pins[0, 107] == 1
#     assert model.pins[1, 1] == 1
#     assert model.pins[1, 12] == 1
#     assert model.pins[7, 1] == 1


def test_convolution():
    a = np.array([0, 0, 0, 0, -1, 0, 1, 0, 0])
    b = np.array([1, 1, 1])

    c = np.convolve(a, b)
    print(c)
