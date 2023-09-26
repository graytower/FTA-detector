import os
import time
import copy
import socket
import random

import redis

import get_mcs


class MyLocator:

    def __init__(self):

        self.faulty_path_list = []
        self.repaired_path_list = []
        self.repaired_link_list = set()
    
    # def GenFalutyLink(self, faulty_link_num, faulty_spine_leaf_link_prob):

    #     faulty_spine_leaf_link_num = 0
    #     for faulty_link_num_tmp in range(faulty_link_num):
    #         if(random.randrange(10) < 10*faulty_spine_leaf_link_prob):
    #             faulty_spine_leaf_link_num += 1

    #     faulty_leaf_tor_link_num = faulty_link_num - faulty_spine_leaf_link_num

    #     spine_leaf_link_failed_list = random.sample(
    #         spine_leaf_link_list, faulty_spine_leaf_link_num)
    #     leaf_tor_link_failed_list = random.sample(
    #         leaf_tor_link_list, faulty_leaf_tor_link_num)

    #     faulty_link_list = spine_leaf_link_failed_list + leaf_tor_link_failed_list

    #     return faulty_link_list


    def RecvFaultyPath(self):

        r = redis.Redis(unix_socket_path='/var/run/redis/redis-server.sock')
        pubsub = r.pubsub()
        pubsub.psubscribe('__keyevent@0__:expired')

        no_failure = True
        failure_begin = time.time()
        while(no_failure or time.time()-failure_begin<10):

            message = pubsub.get_message()

            if(message != None and message['pattern'] == '__keyevent@0__:expired'):
                
                if(no_failure == True):
                    no_failure = False
                    failure_begin = time.time()

                sw_port = message['data'].split('--')[3:-1]
                faulty_path = []

                for i in range(0, len(sw_port), 2):
                    faulty_link = [sw_port[i], sw_port[i+1]]
                    faulty_link.sort()
                    faulty_path.append(
                        faulty_link[0] + '--' + faulty_link[1])

                self.faulty_path_list.append(faulty_path)
        
        print("Faulty paths are:\n")
        print(self.faulty_path_list)
        print("\n")


    def RecvRepairedPath(self):

        r = redis.Redis(unix_socket_path='/var/run/redis/redis-server.sock')
        pubsub = r.pubsub()
        pubsub.psubscribe('__keyevent@0__:set')

        no_repaire = True
        repaire_begin = time.time()
        while(no_repaire or time.time()-repaire_begin < 10):

            message = pubsub.get_message()

            if(message != None and message['pattern'] == '__keyevent@0__:set'):

                if(no_repaire == True):
                    no_repaire = False
                    repaire_begin = time.time()

                sw_port = message['data'].split('--')[3:-1]
                repaired_path = []

                for i in range(0, len(sw_port), 2):
                    repaired_link = [sw_port[i], sw_port[i+1]]
                    repaired_link.sort()
                    repaired_path.append(
                        repaired_link[0] + '--' + repaired_link[1])
                    self.repaired_link_list.add(
                        repaired_link[0] + '--' + repaired_link[1])

                self.repaired_path_list.append(repaired_path)
            
        print("Paths repaired:\n")
        print(self.repaired_path_list)
        print("\n")


    def AdjustFaultyPath(self):

        for faulty_path in self.faulty_path_list[::-1]:
            if faulty_path in self.repaired_path_list:
                self.faulty_path_list.remove(faulty_path)


    def LocateFaultyLink(self):

        faulty_path_list = copy.deepcopy(self.faulty_path_list)

        for faulty_path in faulty_path_list[::-1]:
            for faulty_link in faulty_path[::-1]:
                if faulty_link in self.repaired_link_list:
                    faulty_path.remove(faulty_link)

            if faulty_path == []:
                faulty_path_list.remove([])

        mcs_dict = {}
        cs_dict = {}
        # # print(tuple(next_path))
        for faulty_path in faulty_path_list:
            cs_dict = get_mcs.GetCutSet(mcs_dict, tuple(faulty_path), 0.0001)
            mcs_dict = get_mcs.GetMinCutSet(cs_dict)

        print("Probably faulty links:\n")
        print(mcs_dict)
        print("\n")

        return mcs_dict

    # def GetAllLink(self):

    #     r = redis.Redis(
    #         unix_socket_path='/var/run/redis/redis-server.sock', db=1)
    #     link_pair_list = r.keys()
    #     spine_leaf_link_list = []
    #     leaf_tor_link_list = []
    #     for link in link_pair_list:
    #         if r.get(link) == "Spine-Leaf":
    #             spine_leaf_link_list.append(link.split('--'))
    #         elif r.get(link) == "Leaf-ToR":
    #             leaf_tor_link_list.append(link.split('--'))

    #     return spine_leaf_link_list, leaf_tor_link_list


if __name__ == "__main__":

    #######################################
    # For testing
    faulty_path_num_list = []
    round_num_list = []
    time_list = []
    #######################################

    my_locator = MyLocator()
    my_locator.RecvFaultyPath()
    while(my_locator.faulty_path_list!=[]):
        my_locator.LocateFaultyLink()
        my_locator.RecvRepairedPath()
        my_locator.AdjustFaultyPath()
    
    print("Repaired.")




    # # for i in [1, 2, 3]:
    # for i in [2]:
    #     # for j in [0, 0.2, 0.4, 0.6, 0.8, 1]:
    #     for j in [0.4, 0.6, 0.8, 1]:
    #         for k in range(20):

    #             my_locator = MyLocator()

    #             # Get all links
    #             [spine_leaf_link_list, leaf_tor_link_list] = my_locator.GetAllLink()

    #             #######################################
    #             # For testing
    #             round_num = 0
    #             #######################################

    #             # Randomly choose several links as faulty links
    #             faulty_link_num = i
    #             faulty_spine_leaf_link_prob = j
    #             faulty_link_list = my_locator.GenFalutyLink(i, j)
    #             print(faulty_link_list)

    #             for faulty_link in faulty_link_list:
    #                 os.system("sudo python ../topology/link_status_controller.py %s %s down &" %
    #                           (faulty_link[0], faulty_link[1]))

    #             #######################################
    #             # For testing
    #             time_1 = time.time()
    #             #######################################

    #             # Receive faulty paths...
    #             print(i, j, k+1)
    #             print("Start receiving faulty paths...")
    #             my_locator.RecvFaultyPath()
    #             # print(my_locator.faulty_path_list)

    #             #######################################
    #             # For testing
    #             faulty_path_num = len(my_locator.faulty_path_list)
    #             #######################################

    #             # Locate
    #             while True:
    #                 # print(my_locator.repaired_link_list)
    #                 my_locator.AdjustFaultyPath()

    #                 # print("Faulty paths:")
    #                 # print(my_locator.faulty_path_list)
    #                 # print('\n')

    #                 if my_locator.faulty_path_list == []:
    #                     break

    #                 #######################################
    #                 # For testing
    #                 round_num = round_num + 1
    #                 #######################################

    #                 mcs = my_locator.LocateFaultyLink()
    #                 rs = max(mcs, key=mcs.get)
    #                 print(rs)

    #                 print('Repairing...')
    #                 for faulty_link_pair in rs:
    #                     faulty_link_pair = faulty_link_pair.split('--')

    #                     # Add repaired links into repaired_link_list
    #                     my_locator.repaired_link_list.add(
    #                         '%s--%s' % (faulty_link_pair[0], faulty_link_pair[1]))
    #                     my_locator.repaired_link_list.add(
    #                         '%s--%s' % (faulty_link_pair[1], faulty_link_pair[0]))

    #                     node_a = faulty_link_pair[0].split('_')[0]
    #                     node_b = faulty_link_pair[1].split('_')[0]
    #                     os.system("sudo python ../topology/link_status_controller.py %s %s up &" %
    #                               (r.get(node_a), r.get(node_b)))

    #                 my_locator.RecvRepairedPath()

    #             print("Finish\n\n")
    #             #######################################
    #             # For testing
    #             time_2 = time.time()
    #             #######################################

    #             faulty_path_num_list.append(faulty_path_num)
    #             round_num_list.append(round_num)
    #             time_list.append(time_2-time_1)

    #         print("faulty_path_num_list: ", faulty_path_num_list)
    #         print("round_num_list: ", round_num_list)
    #         print("time_list: ", time_list)
