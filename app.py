from __future__ import annotations

import csv
import random
from typing import Union


class DieFace:
    die_face_id: str
    die_face_value: Union[int, None]
    adjacent_die_faces_by_face_id: list[DieFace]

    def __init__(self, die_face_id: str):
        self.die_face_id = die_face_id
        self.die_face_value = None
        self.adjacent_die_faces_by_face_id = {}

    def set_die_face_value(self, die_face_value: Union[int, None]):
        self.die_face_value = die_face_value

    def add_adjacent_die_face(self, adjacent_die_face: DieFace):
        if adjacent_die_face.die_face_id not in self.adjacent_die_faces_by_face_id.keys():
            self.adjacent_die_faces_by_face_id[adjacent_die_face.die_face_id] = adjacent_die_face

    def remove_adjacent_die_face(self, adjacent_die_face: DieFace):
        if adjacent_die_face.die_face_id in self.adjacent_die_faces_by_face_id.keys():
            del self.adjacent_die_faces_by_face_id[adjacent_die_face.die_face_id]

    def get_adjacent_die_face_value_sum(self) -> int:
        adjacent_die_faces: list[DieFace] = self.adjacent_die_faces_by_face_id.values(
        )
        adjacent_sum: int = 0
        for adjacent_die_face in adjacent_die_faces:
            adjacent_sum += adjacent_die_face.die_face_value
        return adjacent_sum

    def get_adjacent_die_face_count(self) -> int:
        adjacent_die_faces: list[DieFace] = self.adjacent_die_faces_by_face_id.values(
        )
        return len(adjacent_die_faces)

    def get_adjacent_die_face_value_mean(self) -> float:
        return self.get_adjacent_die_face_value_sum() / self.get_adjacent_die_face_count()


class Die:
    die_faces_by_die_face_id: dict[str, DieFace]
    die_faces_by_die_vertex_id: dict[str, DieFace]

    def __init__(self):
        self.die_faces_by_die_face_id = {}
        self.die_faces_by_die_vertex_id = {}

    def load(self, die_faces_file_path: str, die_vertices_file_path: str):
        self._load_die_faces_from_file(die_faces_file_path=die_faces_file_path)
        self._load_die_vertices_from_file(
            die_vertices_file_path=die_vertices_file_path)
        self.sequence_die_face_values()

    def _load_die_vertices_from_file(self, die_vertices_file_path: str):
        with open(die_vertices_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                die_face_id: str = row['die_face_id']
                die_vertex_id: str = row['die_vertex_id']
                # print("face " + die_face_id + " -> vertex " + die_vertex_id)
                if die_face_id not in self.die_faces_by_die_face_id.keys():
                    raise Exception(f'Missing die face: { die_face_id }')
                else:
                    die_face = self.die_faces_by_die_face_id[die_face_id]
                    self.die_faces_by_die_vertex_id[die_vertex_id] = die_face

    def _load_die_faces_from_file(self, die_faces_file_path: str):
        with open(die_faces_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                from_die_face_id: str = row['from_die_face_id']
                to_die_face_id: str = row['to_die_face_id']
                # print("face " + from_die_face_id +
                #       " -> face " + to_die_face_id)
                if from_die_face_id not in self.die_faces_by_die_face_id.keys():
                    self.die_faces_by_die_face_id[from_die_face_id] = DieFace(
                        die_face_id=from_die_face_id)
                if to_die_face_id not in self.die_faces_by_die_face_id.keys():
                    self.die_faces_by_die_face_id[to_die_face_id] = DieFace(
                        die_face_id=to_die_face_id)
                from_face = self.die_faces_by_die_face_id[from_die_face_id]
                to_face = self.die_faces_by_die_face_id[to_die_face_id]
                from_face.add_adjacent_die_face(adjacent_die_face=to_face)

    def sequence_die_face_values(self, die_faces: Union[list[DieFace], None] = None):
        if die_faces is None:
            die_faces = self.die_faces_by_die_face_id.values()
        i = 1
        for die_face in die_faces:
            die_face.set_die_face_value(i)
            i += 1

    def randomize_die_face_values(self):
        die_faces = list(self.die_faces_by_die_face_id.values())
        random.shuffle(die_faces)
        self.sequence_die_face_values(die_faces=die_faces)

    def clone(self) -> Die:
        die = Die()
        die.die_faces_by_die_face_id = self.die_faces_by_die_face_id.copy()
        die.die_faces_by_die_vertex_id = self.die_faces_by_die_vertex_id
        return die

    def clone_with_random_die_face_values(self) -> Die:
        die = self.clone()
        die.randomize_die_face_values()
        return die

    def get_expected_face_value(self) -> float:
        # assumes that all the face values are sequentially ordered from 1 to N and that each face has the same probability
        die_faces = self.die_faces_by_die_face_id.values()
        if set([die_face.die_face_value for die_face in die_faces]) != set(range(1, len(die_faces) + 1)):
            raise Exception(
                "expected value of face values violates the assumption that the face values are sequentially ordered from 1 to N")

        die_face_count = len(die_faces)
        return (die_face_count + 1) / 2

    def get_die_face_value_error(self):
        expected_face_value: float = self.get_expected_face_value()
        die_faces = self.die_faces_by_die_face_id.values()
        die_face_value_error: float = 0.0
        for die_face in die_faces:
            die_face_value_error += abs(
                die_face.get_adjacent_die_face_value_mean() - expected_face_value)
        die_face_value_error = die_face_value_error / len(die_faces)
        return die_face_value_error

    def stats(self):
        die_faces = self.die_faces_by_die_face_id.values()
        print("")
        for die_face in die_faces:
            adjacent_die_faces = die_face.adjacent_die_faces_by_face_id.values()
            for adjacent_die_face in adjacent_die_faces:
                print("face " + die_face.die_face_id + " ( " + str(die_face.die_face_value) + " ) "
                      " -> face " + adjacent_die_face.die_face_id + " ( " + str(adjacent_die_face.die_face_value) + " ) ")
            print("face id " + die_face.die_face_id + " -> face sum = " +
                  str(die_face.get_adjacent_die_face_value_sum()))
        print("")
        for die_face in die_faces:
            print("face id " + die_face.die_face_id + " -> face mean = " +
                  str(die_face.get_adjacent_die_face_value_mean()))
        print("expected face value: " + str(self.get_expected_face_value()))
        print("error for faces " + str(self.get_die_face_value_error()))


def main():
    D20_FACES_FILE_PATH = "data/d20_faces.csv"
    D20_VERTICES_FILE_PATH = "data/d20_vertices.csv"
    dice = []
    max_dice = 10000
    for i in range(max_dice):
        die = Die()
        die.load(die_faces_file_path=D20_FACES_FILE_PATH,
                 die_vertices_file_path=D20_VERTICES_FILE_PATH)
        die.randomize_die_face_values()
        dice.append(die)
    best_dice = None
    best_die_error = None
    for die in dice:
        die_error = die.get_die_face_value_error()
        if best_dice is None:
            best_dice = [die]
            best_die_error = die_error
        else:
            if best_die_error is not None:
                if die_error < best_die_error:
                    best_dice = [die]
                    best_die_error = die_error
                elif die_error == best_die_error:
                    best_dice.append(die)
    for best_die in best_dice:
        best_die.stats()


if __name__ == "__main__":
    main()
