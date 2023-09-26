# Eg. rs_dict = {(1, 2, 3) : 0, (2, 3, 4) : 0, (3, 4, 5) : 0}, input_tuple = (1, 2, 4)
def GetCutSet(mcs_dict, next_path, threshold):

    cs_dict = {}

    # Init
    if mcs_dict == {}:

        for i in next_path:

            cs = []
            cs_prob = 1

            cs.append(i)
            cs_prob = cs_prob * 0.1

            # Remove cs of whose prob < threshold
            if cs_prob < threshold:
                break

            cs = tuple(cs)
            cs_dict[cs] = cs_prob

    else:
        # Mininum cut set of the last round
        mcs = mcs_dict.keys()

        # Eg. i = (1, 2, 3), j = 1
        for i in mcs:
            for j in next_path:

                cs = list(i)
                cs_prob = mcs_dict[i]

                # If j in i, cs will be i, else, cs will be i combines j
                if (j not in i):
                    cs.append(j)
                    cs_prob = cs_prob * 0.1

                    if cs_prob < threshold:
                        break

                cs = tuple(cs)

                cs_dict[cs] = cs_prob
                # print(cs, cs_prob)

    return cs_dict


def GetMinCutSet(cs_dict):

    mcs_dict = {}

    cs = cs_dict.keys()

    index_1 = 0
    while index_1 < len(cs):

        set_1 = set(cs[index_1])

        index_2 = index_1 + 1
        while index_2 < len(cs):

            set_2 = set(cs[index_2])

            # Get the same part of set_1 and set_2
            inter_set_1_set_2 = set.intersection(set_1, set_2)

            # If and set_2 contains set_1
            if inter_set_1_set_2 == set_1:

                # Delete set_2 from dict and keys, and index_2 = current value
                cs_dict.pop(cs[index_2])
                cs.pop(index_2)

            # Elif the size of set_i is bigger, and set_i contains set_j
            elif inter_set_1_set_2 == set_2:

                # Delete set_1 from dict and keys, and index_1 = current_value
                cs_dict.pop(cs[index_1])
                cs.pop(index_1)

                # Restart, goto index_1 += 1 to make it equal 0
                index_1 = -1
                break

            else:
                index_2 += 1

        # index_2 iteration finish, index_1 ++
        index_1 += 1

    mcs_dict = cs_dict

    return mcs_dict
