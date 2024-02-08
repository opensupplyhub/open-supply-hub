class ListParser:
    def __init__(self):
        pass

    def parse(self, my_list):
        my_dict = {}
        for item in my_list:
            key = item[0]
            value = item[1]
            my_dict[key] = value
        return my_dict

   