import os
import json
from typing import Optional, List, Union
import numpy as np
import spacy


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

    PATH: str = os.path.join(os.sep, 'tmp', 'en_benji_custom')
    DEFAULT: str = 'en_core_web_md'

    def __init__(self):
        """
        Lazy constructor.
        """
        self._word: str = ''
        self._array: Optional[np.array] = None

    @classmethod
    @property
    def model(cls) -> 'spacy.lang.en.English':
        """
        Loads the SpaCy model from disk.
        """
        if not hasattr(cls, '_model'):
            try: 
                cls._model: 'spacy.lang.en.English' = spacy.load(cls.PATH)
            except IOError:
                cls._model = spacy.load(cls.DEFAULT)
        return cls._model

    @classmethod
    @property
    def size(cls) -> int:
        """
        Returns the size of a vector.
        """
        vector: Vector = Vector()
        vector.word = 'dummy'
        return len(vector.array)

    @property
    def array(self) -> np.array:
        """
        Numpy vector getter.
        """
        if self._array is None and self.word:
            self._array = self.model(self.word).vector
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
        return not self.word or self.model.vocab[self.word].is_stop

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

    @classmethod
    def train(cls, terms: Union[str, List[str]]) -> List['Vector']:
        """
        Trains SpaCy with new words.
        https://spacy.io/api/vocab#set_vector
        """
        vectors: List['Vector'] = cls.to_vectors(terms)
        for vector in vectors:
            if not vector.is_known():
                vector.array = cls.generate_random_vector()
                cls.model.vocab.set_vector(vector.word, vector.array)
        Vector.model.to_disk(Vector.PATH)
        return vectors

    @classmethod
    def generate_random_vector(cls) -> np.array:
        """
        Generates a random vector for a new word.
        """
        array: np.array = np.random.rand(cls.size, )
        array[0] = 3.14  # All unknowns together.
        return array

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
        return self.word and not isinstance(self.array, str) and self.array.any() and self.word in self.model.vocab
