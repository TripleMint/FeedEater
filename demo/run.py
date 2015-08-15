import sys
import os
path = os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0]
print path
sys.path.append(path)

print sys.path
from FeedEater import FeedEater
from FeedEater.normalize import DataCleansingModelProxy
from FeedEater.translate import field, Translator
import csv, json


import inspect


files_path = os.path.dirname(os.path.abspath(__file__))
input_paths = [os.path.join(files_path, 'source.csv'),
               os.path.join(files_path, 'source.json')]


class Person(object):

    def __init__(self):

        self._first_name = ''
        self._last_name = ''
        self.location = ''
        self.profession = ''

    def load(self):

        file_path = os.path.join(files_path, self.first_name + self.last_name)
        with open(file_path, 'r') as f:
            first, last, location, profession = f.read().split(' ')
        self.first_name = first
        self.last_name = last
        self.location = location
        self.profession = profession

    @property
    def first_name(self):

        return self._first_name

    @first_name.setter
    def first_name(self, value):

        print 'fn', value
        for frame in inspect.stack():
            print frame
        self._first_name = value

    @property
    def last_name(self):

        return self._last_name

    @last_name.setter
    def last_name(self, value):

        print 'ln', value
        for frame in inspect.stack():
            print frame
        self._last_name = value

    def save(self):

        file_path = os.path.join(files_path, self.first_name + self.last_name)
        print file_path
        with open(file_path, 'w') as f:
            f.write(' '.join([self.first_name,
                              self.last_name,
                              self.location,
                              self.profession]))

def normalize_name(name):

    print 'n', name
    if name:
        print name[0].upper() + name[1:].lower()
        return name[0].upper() + name[1:].lower()
    else:
        print name
        return name

class PersonProxy(DataCleansingModelProxy):

    model = Person

    def first_name(self, value):

        return normalize_name(value)

    def last_name(self, value):

        return normalize_name(value)

    @classmethod
    def get_or_create(cls, first_name, last_name):

        person = Person()
        person.first_name = normalize_name(first_name)
        person.last_name = normalize_name(last_name)
        print 'gc', person.first_name, person.last_name
        try:
            person.load()
        except IOError:
            pass
        return cls(person)


def get_json_people():

    with open(input_paths[1], 'r') as f:
        out = json.load(f)
    return out

class PersonJsonTranslator(Translator):

    model = PersonProxy
    feed = staticmethod(get_json_people)

    @field
    def first_name(self):

        return self.input['first_name']

    @field
    def last_name(self):

        return self.input['last_name']

    @field
    def location(self):

        return self.input['location']

    def get_model_instance(self, input_=None):

        if input_:
            self.input = input_
        inst = self.model.get_or_create(self.input['first_name'],
                                        self.input['last_name'])
        self.model_instance = inst
        return inst


def get_csv_people():

    with open(input_paths[0], 'r') as f:
        out = [row for row in csv.reader(f)]
    return out

class PersonCsvTranslator(Translator):

    model = PersonProxy
    feed = staticmethod(get_csv_people)

    @field
    def first_name(self):

        return self.input[1]

    @field
    def last_name(self):

        return self.input[0]

    @field
    def profession(self):

        return self.input[3]

    def get_model_instance(self, input_=None):

        if input_:
            self.input = input_
        inst = self.model.get_or_create(self.input[1],
                                        self.input[0])
        self.model_instance = inst
        return inst


class PersonJsonEater(FeedEater):

    translator_class = PersonJsonTranslator
    continue_on_errors = ()


class PersonCsvEater(FeedEater):

    translator_class = PersonCsvTranslator
    continue_on_errors = ()


PersonJsonEater().eat()
PersonCsvEater().eat()