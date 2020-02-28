import numpy as np
import math
import os
from numpy import *
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform
import pathlib


ALPHABET = {'A': 'ALA', 'F': 'PHE', 'C': 'CYS', 'D': 'ASP', 'N': 'ASN',
            'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS', 'L': 'LEU',
            'I': 'ILE', 'K': 'LYS', 'M': 'MET', 'P': 'PRO', 'R': 'ARG',
            'S': 'SER', 'T': 'THR', 'V': 'VAL', 'W': 'TRP', 'Y': 'TYR'}
AA_HYDROPATHICITY_INDEX = {'ARG': -4.5, 'LYS': -3.9, 'ASN': -3.5, 'ASP': -3.5, 'GLN': -3.5,
                           'GLU': -3.5, 'HIS': -3.2, 'PRO': -1.6, 'TYR': -1.3, 'TRP': -0.9,
                           'SER': -0.8, 'THR': -0.7, 'GLY': -0.4, 'ALA': 1.8, 'MET': 1.9,
                           'CYS': 2.5, 'PHE': 2.8, 'LEU': 3.8, 'VAL': 4.2, 'ILE': 4.5}
AA_BULKINESS_INDEX = {'ARG': 14.28, 'LYS': 15.71, 'ASN': 12.82, 'ASP': 11.68, 'GLN': 14.45,
                      'GLU': 13.57, 'HIS': 13.69,  'PRO': 17.43, 'TYR': 18.03, 'TRP': 21.67,
                      'SER': 9.47, 'THR': 15.77, 'GLY': 3.4, 'ALA': 11.5, 'MET': 16.25,
                      'CYS': 13.46, 'PHE': 19.8, 'LEU': 21.4, 'VAL': 21.57, 'ILE': 21.4}
AA_FLEXIBILITY_INDEX = {'ARG': 2.6, 'LYS': 1.9, 'ASN': 14., 'ASP': 12., 'GLN': 4.8,
                        'GLU': 5.4, 'HIS': 4., 'PRO': 0.05, 'TYR': 0.05, 'TRP': 0.05,
                        'SER': 19., 'THR': 9.3, 'GLY': 23., 'ALA': 14., 'MET': 0.05,
                        'CYS': 0.05, 'PHE': 7.5, 'LEU': 5.1, 'VAL': 2.6, 'ILE': 1.6}
AA_MESSAGE = {}
for aa_short in ALPHABET.keys():
    aa_long = ALPHABET[aa_short]
    AA_MESSAGE.update({aa_short: [(5.5 - AA_HYDROPATHICITY_INDEX[aa_long]) / 10,
                                  AA_BULKINESS_INDEX[aa_long] / 21.67,
                                  (25. - AA_FLEXIBILITY_INDEX[aa_long]) / 25.]})
    AA_MESSAGE.update({aa_long: [(5.5 - AA_HYDROPATHICITY_INDEX[aa_long]) / 10,
                                 AA_BULKINESS_INDEX[aa_long] / 21.67,
                                 (25. - AA_FLEXIBILITY_INDEX[aa_long]) / 25.]})
DISTANCE_WINDOW_PATH = 'D:\\database\\rmsd_compare\\real'
# filename = input()
# path = os.path.join(os.getcwd(),filename)
path = 'D:\\database\\rmsd_compare\\real\\4f7v.pdb'

#提取CA原子信息
def atoms_infos(path):
    file = open(path, 'r')
    lines = file.readlines()

    atoms_info = [line.strip('\n') for line in lines if line.split()[0] == 'ATOM' and line.split()[2] == 'CA']
    delet = []
    # 筛掉重复概率小的氨基酸
    for i in range(len(atoms_info)):
        if atoms_info[i - 1].split()[2] == atoms_info[i].split()[2] and atoms_info[i - 1].split()[5] == atoms_info[i].split()[5]:
            if atoms_info[i - 1].split()[-3] <= atoms_info[i].split()[-3]:
                delet.append(i - 1)
            else:
                delet.append(i)
    for i in delet[::-1]:
        del atoms_info[i]
    # atoms_info = array(atoms_info)
    return atoms_info

#断链情况是否进行补全

#提取坐标信息
def extract_coord(atoms_info):
    coord_array = np.zeros((len(atoms_info), 3))
    acid_list = []
    for i in range(len(atoms_info)):
        coord_array[i] = [float(atoms_info[i].split()[j]) for j in range(6, 9)]
        acid_list.append(atoms_info[i].split()[3][-3::])
    acid_array = array(acid_list)
    return coord_array, acid_array


def torsion():
    for n in range(len(torsion_sin)):
        torsion_training[n] = math.atan2(torsion_sin[n], torsion_cos[n])

def distance_window(coord_array, acid_array):
    WINDOW_SIZE = 15
    distCA = pdist(coord_array, metric='euclidean')
    distCA = squareform(distCA).astype('float32')
    save_name = 'out.npy'
    mark_type = [('distance', float), ('aa', 'S10')]
    dist_windows = []

    for i in range(len(distCA)):
        marked_array = []
        new_array = []
        for j in range(len(distCA[i])):
            marked_array.append((distCA[i, j], acid_array[j]))
        marked_array = np.array(marked_array, dtype=mark_type)
        marked_array = np.sort(marked_array, order='distance')[:WINDOW_SIZE]
        for j in range(len(marked_array)):
            aa = marked_array[j][1].decode('utf-8')
            new_array.append([marked_array[j][0]] + AA_MESSAGE[aa])
        dist_windows.append(new_array)
    dist_windows = np.array(dist_windows).astype('float32')

    np.save(os.path.join(DISTANCE_WINDOW_PATH, save_name), dist_windows)
    print('successful')

if __name__ == "__main__":
    atoms_info = atoms_infos(path)
    coord_array, acid_array = extract_coord(atoms_info)
    distance_window(coord_array, acid_array)
