from .object_factory import ObjectFactory
from .services.festival_service import FestivalBuilder


class TTSServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


services = TTSServiceProvider()
services.register_builder("DEFAULT", FestivalBuilder())
services.register_builder("FESTIVAL", FestivalBuilder())
