class ListMembershipHashTable:
    def __init__(self):
        self.table_size = 1000003
        self.table = [None for _ in range(self.table_size)]
        pass

    def h(self, key):
        return hash(key) % self.table_size

    # def search(self, key):
    #     idx = self.h(key)
    #     if self.table[idx] is None:
    #         return []
    #     # found_rec = (lambda x: x[0] if len(x) > 0 else [])(
    #     #     [i for i in self.table[idx] if len(i) > 0 and i[0] == key])
    #     found_rec = self.table[idx][key] if key in self.table[idx] else []
    #
    #     return found_rec

    def find_all(self, key):
        idx = self.h(key)
        if self.table[idx] is None:
            return []
        # found_recs = (lambda x: x if len(x) > 0 else [])(
        #     [i for i in self.table[idx] if len(i) > 0 and i[0] == key])
        found_recs = self.table[idx][key] if key in self.table[idx] else []

        return found_recs

    def insert(self, line, key):
        idx = self.h(key)
        if self.table[idx] is None:
            # self.table[idx] = [[key, line]]
            self.table[idx] = {key: [line]}

        # found_rec = (lambda x: x[0] if len(x) > 0 else [])(
        #     [i for i in self.table[idx] if len(i) > 0 and i[0][0] == key])

        found_rec = self.table[idx][key] if key in self.table[idx] else []

        if len(found_rec) > 0:  # This means key found
            # if [key, line] not in found_rec:  # record not found. Insert.
            #     found_rec.append([key, line])
            if line not in found_rec:  # record not found. Insert.
                found_rec.append(line)
        else:
            # self.table[idx] = [[key, line]]
            self.table[idx][key] = [line]


