import time as t
import copy as cp
import random as rn
import re

import handle_data.ConstantsAndUtil as ConstUtil


def eliminate_bad_commas(line):
    li = line.split('"', 2)
    while len(li) == 3:
        li = li[0] + li[1].replace(',', ' _AND_') + li[2]
        li = li.split('"', 2)

    return li[0]


def read_file_into_dicts(filename):
    dicts = []

    with open(filename, 'r') as f:
        first_line = f.readline().split(',')
        # print(first_line)

        for line in f:

            parsed_line = eliminate_bad_commas(line).split(',')
            dicts.append({})
            # line = f.readline()
            # line = f.readline().split(',')
            # if 'new_Dir' in filename:
            #     print(filename, line)
            for idx, itm in enumerate(first_line):
                # if len(parsed_line)<=idx:
                #     print(len(parsed_line),idx)
                #     print(parsed_line)
                if parsed_line[idx].endswith('.0'):
                    dicts[-1][itm.replace('\n', '')] = parsed_line[idx].split('.0')[0]
                else:
                    dicts[-1][itm.replace('\n', '')] = parsed_line[idx]
            # if 'new_Dir' in filename:
            #     print(dicts[-1])

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

        the_dict['list_of_dmcs_len'] = len(the_dict['list_of_dmcs'])  # for extra length data.

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
    c = 0
    for i in company_data:
        print(c)
        c += 1
        i["director_list"] = []
        i["director_list_len"] = ''  # for extra length data.
        jdx = 0
        while jdx < len(director_data):
            if director_data[jdx]["group_comp_id"] == i["group_comp_id"] and director_data[jdx]["fyear"] == i["fyear"]:
                i["director_list"].append(director_data[jdx]["dir_id"])
            jdx += 1
        # print(len(i["director_list"]))
        i["director_list_len"] = len(i["director_list"])  # for extra length data.
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

                    # Add list sizes
                    # f.write(',')
                    # f.write(str(len(value)))

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
                elif itm in ['fyear', 'log_ta', 'mtb', 'debtat', 'roa'] and parsed_line[idx] is not '':
                    try:
                        if re.match(r'-?\d+', parsed_line[idx])[0] == parsed_line[idx]:
                            company_and_director_data[-1][itm.replace('\n', '')] = int(parsed_line[idx])
                        elif re.match(r'-?\d+[.]\d+', parsed_line[idx])[0] == parsed_line[idx]:
                            company_and_director_data[-1][itm.replace('\n', '')] = float(parsed_line[idx])
                        elif re.match(r'-?\d[.]\d+[eE]-\d+', parsed_line[idx])[0] == parsed_line[idx]:
                            company_and_director_data[-1][itm.replace('\n', '')] = float(parsed_line[idx])
                        elif re.match(r'-?\d[.]\d+[eE]\+\d+', parsed_line[idx])[0] == parsed_line[idx]:
                            company_and_director_data[-1][itm.replace('\n', '')] = float(parsed_line[idx])
                    except Exception:
                        print(re.match(r'-?\d[.]\d+[eE]-\d+', parsed_line[idx]))
                        print(itm, parsed_line[idx], idx)
                        print(type(parsed_line[idx]))
                        raise

                elif itm is not '\n':
                    company_and_director_data[-1][itm.replace('\n', '')] = parsed_line[idx]


if __name__ == "__main__":
    main_dir = ConstUtil._main_dir
    _company_filename = main_dir + "data/new_Comp.csv"
    _director_filename = main_dir + "data/new_Dir.csv"

    make_merged_data = True
    cut_from_merged_data = True

    t1 = t.time()

    if make_merged_data:

        # _company_data = read_file_into_dicts(_company_filename)
        # _company_data_fixed = fix_company_data(_company_data)
        # _director_data = read_file_into_dicts(_director_filename)
        # _director_data_fixed = fix_company_data(_director_data)

        _company_data_fixed = fix_company_data(read_file_into_dicts(_company_filename))
        _director_data_fixed = fix_director_data(read_file_into_dicts(_director_filename))

        # print(_company_data_fixed[0]['group_comp_id'])
        # print(_company_data_fixed == sorted(_company_data_fixed, key=lambda xx: xx['group_comp_id']))
        # for _i in range(1000):
        #     if rn.random() < 0.02:
        #         print(_director_data_fixed[_i]['dir_id'])

        _company_and_director_data = merge_company_director_data(_company_data_fixed, _director_data_fixed)
        # group_comp_id
        # dir_id
        # fyear

        _company_data_fixed = _director_data_fixed = None

        save_data_file(_company_and_director_data, main_dir + "data/merged_extended_data.csv")

        # _company_and_director_data2 = []
        # load_data_file(_company_and_director_data2, main_dir + "data/merged_data.csv")

        # print(_company_and_director_data[7] == _company_and_director_data2[7])
        # print(_company_and_director_data[7])
        # print(_company_and_director_data2[7])

    if cut_from_merged_data:
        _company_and_director_data = []
        load_data_file(_company_and_director_data, main_dir + "data/merged_extended_data.csv")

        cut_data = []
        for _line in _company_and_director_data:
            if _line['dam_stock'] in ['0', '1']:
                cut_data.append(_line)
        save_data_file(cut_data, main_dir + "data/merged_ext_data_dam_stock.csv")


    t2 = t.time()

    print('Runtime = %.5f' % (t2 - t1))
