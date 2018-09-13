import time as t
import copy as cp

_main_dir = "C:/Users/User/PycharmProjects/Directors_cut/"


def read_file_into_dicts(filename):
    dicts = []

    with open(filename, 'r') as f:
        first_line = f.readline().split(',')
        # print(first_line)

        for line in f:
            parsed_line = line.split(',')
            dicts.append({})
            # line = f.readline()
            # line = f.readline().split(',')
            # print(line)
            for idx, itm in enumerate(first_line):
                # dicts[-1][itm.replace('\n', '')] = parsed_line[idx]
                dicts[-1][ itm.replace('\n', '') ] = parsed_line[ idx ].split('.0')[0]
            # print(dicts[-1])

    return dicts


def fix_company_data(data):
    for the_dict in data:
        # print(len(the_dict))
        the_dict.__delitem__('')
        the_dict.__delitem__('comp_id')
        the_dict['list_of_dmcs'] = []
        for key, value in list(the_dict.items()):
            if key.startswith('dmc'):
                # if the_dict[key] == '1.0':
                if the_dict[key] == '1':
                    the_dict['list_of_dmcs'].append(key[3:])
                the_dict.__delitem__(key)

        # print("dmcs: %s", str(the_dict['list_of_dmcs']))
        # print(len(the_dict))
        # input()

    return data


def fix_director_data(data):
    for the_dict in data:
        # print(len(the_dict))
        the_dict.__delitem__('')
        the_dict.__delitem__('comp_id')

        # print("dmcs: %s", str(the_dict['list_of_dmcs']))
        # print(len(the_dict))
        # input()

    return data


def merge_company_director_data(company_data, director_data):
    jdx = 0
    for i in company_data:
        i["director_list"] = []
        while jdx < len(director_data) and director_data[jdx]["group_comp_id"] == i["group_comp_id"] and \
                director_data[jdx]["fyear"] == i["fyear"]:
            i["director_list"].append(director_data[jdx]["dir_id"])
            jdx += 1
        # print(len(i["director_list"]))
    return cp.deepcopy(company_data)


def save_data_file(company_and_director_data, filename):
    with open(filename, 'w') as f:
        for i in list(company_and_director_data[0].keys()):
            f.write(str(i)+',')

        f.write('\n')

        for i in company_and_director_data:
            for key, value in i.items():
                if type(value) is list:
                    for j in value:
                        f.write(str(j).replace("\n", "") + '&')
                    f.write('&')
                else:
                    f.write(str(value).replace("\n", ""))
                f.write(',')
            f.write('\n')

            # if [key1 for key1, _ in company_and_director_data[0].items()] == list(i.keys()):
            #     # print("True")
            #     pass
            # else:
            #     print("False")

    pass


def load_data_file(company_and_director_data, filename):
    with open(filename, 'r') as f:
        first_line = f.readline().split(',')

        for line in f:
            parsed_line = line.split(',')
            company_and_director_data.append({})
            for idx, itm in enumerate(first_line):
                if '&' in parsed_line[idx]:
                    if parsed_line[idx] == '&':
                        company_and_director_data[-1][itm.replace('\n', '')] = []
                    else:
                        company_and_director_data[-1][itm.replace('\n', '')] = parsed_line[idx].replace(
                            '&&', '').split('&')
                elif itm is not '\n':
                    company_and_director_data[-1][itm.replace('\n', '')] = parsed_line[idx]


if __name__ == "__main__":
    _company_filename = _main_dir + "data/company_data01.csv"
    _director_filename = _main_dir + "data/director_data01.csv"

    t1 = t.time()

    # _company_data = read_file_into_dicts(_company_filename)
    # _company_data_fixed = fix_company_data(_company_data)
    # _director_data = read_file_into_dicts(_director_filename)
    # _director_data_fixed = fix_company_data(_director_data)

    _company_data_fixed = fix_company_data(read_file_into_dicts(_company_filename))
    _director_data_fixed = fix_company_data(read_file_into_dicts(_director_filename))

    # print(_company_data_fixed[0]['group_comp_id'])
    # print(_company_data_fixed == sorted(_company_data_fixed, key=lambda xx: xx['group_comp_id']))

    _company_and_director_data = merge_company_director_data(_company_data_fixed, _director_data_fixed)
    # group_comp_id
    # dir_id
    # fyear

    _company_data_fixed = _director_data_fixed = None

    # save_data_file(_company_and_director_data, _main_dir + "data/merged_data.csv")
    # _company_and_director_data2 = []
    # load_data_file(_company_and_director_data2, _main_dir + "data/merged_data.csv")

    # print(_company_and_director_data[7] == _company_and_director_data2[7])
    # print(_company_and_director_data[7])
    # print(_company_and_director_data2[7])

    t2 = t.time()

    print('Runtime = %.5f' % (t2 - t1))
