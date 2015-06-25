class InsufficientDataForRecord(ValueError):
    pass


def field(func):

    def field_writer(translator):

        setattr(translator.model_instance, func.__name__, func(translator))

    return field_writer

def metafield(func):

    def field_writer(translator):

        result = func(translator)
        try:
            model_method = getattr(translator.model_instance, func.__name__)
        except AttributeError:
            pass
        else:
            if isinstance(result, dict):
                model_method(**result)
            else:
                model_method(*result)

    return field_writer


class TranslatorMeta(type):

    def __new__(cls, name, bases, attrs):

        if name != 'Translator':

            # Are both model and feed keys in attrs?
            if not {'model', 'feed'}.issubset(attrs.keys()):
                raise ValueError('Translator classes require model and feed class attributes.')

            handler_names = set()
            for base in bases:
                if issubclass(base, Translator) and base.handler_names:
                    handler_names.update(base.handler_names)

            for attr_name, value in attrs.iteritems():
                try:
                    value_name = value.__name__
                except (SyntaxError, AttributeError):
                    pass
                else:
                    if value_name == 'field_writer':

                        # append attr_name so that we defer method resolution
                        # until call time, so that instances and inheritance
                        # work
                        handler_names.add(attr_name)

            attrs['handler_names'] = handler_names
        return type.__new__(cls, name, bases, attrs)


class Translator(object):
    '''
    Translator objects are responsible for producing a DB model instance from a
    record from a feed.  When translate() is called, all methods decorated
    with @field will be called, with the return value for each method assigned
    to the attribute of the same name of the resulting model. Translator
    methods should not normalize or otherwise clean any data, only retrieve
    it from the record produced by the feed.
    '''

    __metaclass__ = TranslatorMeta

    handler_names = set()

    def __init__(self, input_=None):

        self.input = input_
        if input_:
            self.get_model_instance()
        else:
            self.model_instance = None

    def get_model_instance(self, input_=None):

        if input_ is not None:
            self.input = input_
        self.model_instance = self.__class__.model.objects.create()
        return self.model_instance

    def translate(self, input_=None, model_instance=None):

        if input_ is not None:
            self.input = input_
        if model_instance is None:
            self.get_model_instance()
        else:
            self.model_instance = model_instance
        for handler_name in self.__class__.handler_names:
            getattr(self, handler_name)()
        return self.model_instance
