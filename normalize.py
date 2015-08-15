class DataCleansingModelProxyMeta(type):

    model_proxy_map = {}

    def __new__(cls, name, bases, attrs):

        klass = type.__new__(cls, name, bases, attrs)
        if name != 'DataCleansingModelProxy':
            if 'model' not in attrs:
                raise ValueError('Must define model class attribute.')
            DataCleansingModelProxyMeta.model_proxy_map[attrs['model']] = klass
        return klass


def proxy_for(obj):

    if isinstance(obj, type):
        return DataCleansingModelProxyMeta.model_proxy_map[obj]
    else:
        return DataCleansingModelProxyMeta.model_proxy_map[obj.__class__](obj)


class DataCleansingModelProxy(object):
    '''DataCleansingModelProxy classes are meant to act as filters in front of a DB
       model instance to normalize or otherwise clean up data coming from a feed.
       When an attribute is set through the proxy, if a method of the same name
       as the attribute is declared in the proxy, the data being assigned will be
       passed through the method before being assigned to the attribute on the
       underlying model.  If direct access to the model is required, it is available
       through the "instance" attribute on the proxy object.  Proxy objects will
       return proxy objects for any proxyable attribtes as well.  get_or_create()
       defines how to retrieve or create a model instance in the DB.  The default
       implementation will perform a get on the model with kwargs as filter params,
       then create an instance with the same kwargs if the get fails.'''

    __metaclass__ = DataCleansingModelProxyMeta

    def __init__(self, instance=None):

        self.__dict__['instance'] = instance

    def __setattr__(self, name, value):

        if isinstance(value, DataCleansingModelProxy):
            value = value.instance
        if name in self.__dict__ or name in self.__class__.__dict__:
            attr = getattr(self, name)
            if callable(attr):
                setattr(self.instance, name, attr(value))
            else:
                object.__setattr__(self, name, value)
        else:
            setattr(self.instance, name, value)

    def __getattr__(self, name):

        attr = getattr(self.instance, name)
        if name != 'instance':
            try:
                return proxy_for(attr)
            except KeyError:
                return attr
        else:
            return attr

    @classmethod
    def get_or_create(cls, **kwargs):

        inst = cls()
        for name, value in kwargs.iteritems():
            if name in inst.__dict__:
                kwargs[name] = getattr(inst, name)(value)
        try:
            model_inst = cls.model.objects.get(**kwargs)
        except cls.model.DoesNotExist:
            model_inst = cls.model.objects.create(**kwargs)
        return cls(model_inst)