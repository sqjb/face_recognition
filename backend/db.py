import os.path
import pickle
from dataclasses import dataclass
import numpy as np


@dataclass
class Representation:
    name: str
    image_path: str
    registered_at: int
    descriptor: np.ndarray


class RepresentationDB:
    def __init__(self, file_path: str):
        self.__file = os.path.join(".", "reps.pkl")
        self.__cache = []
        if not os.path.exists(file_path):
            print(f"{file_path} not existed, use default {self.__file}")
        else:
            self.__file = file_path
        # load reps from file
        with open(self.__file, "rb") as f:
            self.__cache = pickle.load(f)

    def add(self, reps: list[Representation] | Representation):
        self.__cache.append(reps)
        try:
            with open(self.__file, "wb") as f:
                pickle.dump(self.__cache, f)
            return True
        except BaseException as e:
            print(e)
            return False

    def find_one(self, rep: np.ndarray, thr: float):
        r_dist = 1000000000.
        r_rep = None
        try:
            for his in self.__cache:
                dist = euclidean_distance(rep, his.descriptor)
                #print(dist, his.name, his.image_path)
                if dist < r_dist and dist <= thr:
                    r_rep = his
                    r_dist = dist
        except BaseException as e:
            print(e)
        finally:
            # print(f"find face in {t2-t1} second")
            return r_dist, r_rep

    def findAll(self):
        return self.__cache, len(self.__cache)

    def find(self, page_no: int, page_size: int):
        start = page_no * page_size
        if 0 <= start < len(self.__cache) and page_size >= 1:
            return self.__cache[start:start + page_size], len(self.__cache)
        else:
            return [], len(self.__cache)


def euclidean_distance(v1: np.ndarray, v2: np.ndarray):
    return np.sqrt(np.sum(np.square(v1 - v2)))
