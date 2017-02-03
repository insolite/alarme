from .essential import Essential


class ActionDescriptor(Essential):

    def __init__(self, app, name, id_, factory, **kwargs):
        super().__init__(app, name, id_)
        self.factory = factory
        self.kwargs = kwargs

    def construct(self, **kwargs):
        final_kwargs = self.kwargs.copy()
        final_kwargs.update(kwargs)
        return self.factory(self.app, self.name, self.id, **final_kwargs)
