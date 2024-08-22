class GenericMethodsMixin:
    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )
        if hasattr(self, "action_serializers"):
            return self.action_serializers.get(self.action, self.serializer_class)
        return self.serializer_class
