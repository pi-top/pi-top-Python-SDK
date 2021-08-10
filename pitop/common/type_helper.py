class TypeHelper:
    @staticmethod
    def is_integer(string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False
