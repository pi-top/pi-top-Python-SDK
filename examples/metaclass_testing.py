class MetaUniverse(type):
    def __new__(mcs, *args, **kwargs):
        print("Metauniverse __new__")
        print(args)
        print(kwargs)
        return super(MetaUniverse, mcs).__new__(mcs, *args, **kwargs)

    def __init__(cls, name, bases, dic):
        print("Metauniverse __init__")
        print(name)
        print(bases)
        print(dic)
        super(MetaUniverse, cls).__init__(name, bases, dic)

    def __call__(cls, *args, **kwargs):
        print("Metauniverse __call__")
        print(args)
        print(kwargs)
        if kwargs.get("size") == 10:
            print("SIZE IS 10")
        return super(MetaUniverse, cls).__call__(*args, **kwargs)


class Base:
    def __init__(self):
        self.x = 10

    def hello(self):
        print("hello")


class Base2:
    def __init__(self, value):
        self.y = value


class World(Base, Base2, metaclass=MetaUniverse):
    def __init__(self, size):
        print("World init")
        self.size = size
        Base.__init__(self)
        Base2.__init__(self, value=1)

    def get_name(self):
        print("my name")


world = World(size=10)
print(world.x)
print(world.y)
world2 = World(size=20)
world3 = World(size=30)
