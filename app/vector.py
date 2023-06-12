import json
from typing import Optional, List, Union
import numpy as np
import spacy

english = spacy.load("en_core_web_md")


class NumpyArrayEncoder(json.JSONEncoder):
    """
    Numpy to JSON adapter.
    """

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Vector:
    """
    Vector class.
    """

    def __init__(self):
        """
        Lazy constructor.
        """
        self._word: str = ''
        self._array: Optional[np.array] = None

    @property
    def array(self) -> np.array:
        """
        Numpy vector getter.
        """
        if self._array is None and self.word:
            self.array = english(self.word).vector
        return self._array

    @array.setter
    def array(self, value: np.array):
        """
        Numpy vector setter.
        """
        self._array = value

    @property
    def word(self) -> str:
        """
        Word getter.
        """
        return self._word

    @word.setter
    def word(self, value: str):
        """
        Word setter.
        """
        self._word = ''.join([
            character
            for character in value.lower().strip()
            if character.isalnum()
        ])

    def is_stop(self) -> bool:
        """
        Evaluates if a word is a stop-word.
        """
        return not self.word or english.vocab[self.word].is_stop

    def to_json(self) -> List[float]:
        """
        JSON serializer.
        """
        return {
            "word": self.word,
            "array": json.dumps(self.array, cls=NumpyArrayEncoder),
        }

    @classmethod
    def load(cls, data: dict) -> 'Vector':
        """
        JSON deserializer.
        """
        vector: 'Vector' = cls()
        vector.word = data.get('word', '')
        vector.array = np.array(json.loads(data.get('array', [])))
        return vector

    @classmethod
    def to_vectors(cls, terms: Union[str, List[str]]) -> List['Vector']:
        """
        Vectorizes a string or list of strings.
        """
        if isinstance(terms, str):
            terms: List[str] = terms.split()
        vectors: List['Vector'] = []
        for term in terms:
            vector: 'Vector' = cls()
            vector.word = term
            if not vector.is_stop():
                print('Vector:', vector.word)
                vectors.append(vector)
        return vectors

    def to_list(self) -> List[float]:
        """
        Casts the vector to a list of float numbers.
        """
        assert self.array.tolist() is not None, self.word
        return [
            float(value)
            for value in self.array.tolist()
        ]

    def is_known(self) -> bool:
        """
        Determines if the vectorized word is known.
        """
        return self.array.any()
