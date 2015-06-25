from FeedEater.translate import InsufficientDataForRecord


class FeedEaterMeta(type):

    continue_on_errors = (InsufficientDataForRecord,)
    save_args = []
    save_kwargs = {}

    def __new__(cls, name, bases, attrs):

        if name != 'FeedEater' and 'translator_class' not in attrs:
            raise TypeError('FeedEater classes must have translator_class'
                            ' class attribute.')
        return type.__new__(cls, name, bases, attrs)


class FeedEater(object):

    __metaclass__ = FeedEaterMeta
    save_args = []
    save_kwargs = {}

    def eat(self):

        continue_on_errors = self.continue_on_errors
        save_args = self.save_args
        save_kwargs = self.save_kwargs
        translator = self.translator_class()
        limiter = self.limiter
        excluder = self.excluder
        before_translate = self.before_translate
        after_translate = self.after_translate
        feed_callable = self.translator_class.feed
        # If the callable is a method (has im_class) but unbound (im_self
        # is None), create an instance of it's class and use that as explicit
        # self to call the unbound callable to generate the feed iterable.
        # Otherwise, it is a pure function or a bound method, so just call it.
        if (hasattr(feed_callable, 'im_class')
           and feed_callable.im_self is None):
            feed = self.translator_class.feed(
                self.translator_class.feed.im_class())
        else:
            feed = feed_callable()
        for record in feed:
            try:
                db_record = translator.get_model_instance(record)
            except continue_on_errors:
                continue
            if limiter(record, db_record):
                break
            if not excluder(record, db_record):
                before_translate(record, db_record)
                translator.translate(model_instance=db_record).save(
                    *save_args, **save_kwargs)
                after_translate(record, db_record)

    def limiter(self, record, db_record):

        return False

    def excluder(self, record, db_record):

        return False

    def before_translate(self, record, db_record):

        pass

    def after_translate(self, record, db_record):
        pass
