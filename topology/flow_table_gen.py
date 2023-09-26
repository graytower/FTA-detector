import os


class flow_table():
    def flow_table_gen(self, nodes_list):

        spine_num = nodes_list[0]
        set_num = nodes_list[1]
        leaf_num = nodes_list[1]
        tor_num = nodes_list[2]
        h_num = nodes_list[3]
        pod_num = nodes_list[4]

        thrift_port = 9090
        sw_id = 1

        with open("dump_flow_table.sh", "w") as f:
            f.write("")

        # spine
        for i in xrange(set_num):
            for j in xrange(spine_num):
                with open("flow_table/s%d_s%d.txt" % (i+1, j+1), "w") as f:
                    for k in xrange(pod_num):
                        f.write(
                            "table_add int_mcast_table do_int_mcast %d => %d\n" % (k+1, k+1))
                        f.write("mc_mgrp_create %d\n" % (k+1))

                        int_mcast_list = [n+1 for n in xrange(pod_num)]
                        int_mcast_list.remove(k+1)
                        int_mcast_list = tuple(int_mcast_list)
                        f.write("mc_node_create %d" % (k))
                        for m in int_mcast_list:
                            f.write(" %d" % m)
                        f.write("\n")
                        f.write("mc_node_associate %d %d\n" % (k+1, k))
                        f.write("\n")
                    f.write("table_add int_table do_int => %d\n" % sw_id)
                    sw_id += 1

                with open("dump_flow_table.sh", "a") as f:
                    f.write("sudo simple_switch_CLI --thrift-port %d <flow_table/s%d_s%d.txt\n" %
                            (thrift_port, i+1, j+1))
                    thrift_port += 1
        # leaf
        for i in xrange(pod_num):
            for j in xrange(leaf_num):
                with open("flow_table/p%d_l%d.txt" % (i+1, j+1), "w") as f:
                    for k in xrange(spine_num):
                        f.write(
                            "table_add int_mcast_table do_int_mcast %d => 1\n" % (k+1))
                    temp = 2
                    for k in xrange(spine_num, spine_num+tor_num):
                        f.write(
                            "table_add int_mcast_table do_int_mcast %d => %d\n" % (k+1, temp))
                        temp += 1
                    f.write("\n")

                    f.write("mc_mgrp_create 1\n")
                    int_mcast_list = [
                        n+1 for n in xrange(spine_num, spine_num+tor_num)]
                    int_mcast_list = tuple(int_mcast_list)
                    f.write("mc_node_create 0")
                    for m in int_mcast_list:
                        f.write(" %d" % m)
                    f.write("\n")
                    f.write("mc_node_associate 1 0\n")
                    f.write("\n")

                    temp = 2
                    for k in xrange(spine_num, spine_num+tor_num):
                        f.write("mc_mgrp_create %d\n" % temp)
                        int_mcast_list = [
                            n+1 for n in xrange(spine_num+tor_num)]
                        int_mcast_list.remove(k+1)
                        int_mcast_list = tuple(int_mcast_list)
                        f.write("mc_node_create %d" % (temp-1))
                        for m in int_mcast_list:
                            f.write(" %d" % m)
                        f.write("\n")
                        f.write("mc_node_associate %d %d\n" % (temp, temp-1))
                        f.write("\n")
                        temp += 1

                    f.write("table_add int_table do_int => %d\n" % sw_id)
                    sw_id += 1

                with open("dump_flow_table.sh", "a") as f:
                    f.write("sudo simple_switch_CLI --thrift-port %d <flow_table/p%d_l%d.txt\n" %
                            (thrift_port, i+1, j+1))
                    thrift_port += 1

        # tor
        for i in xrange(pod_num):
            for j in xrange(tor_num):
                with open("flow_table/p%d_t%d.txt" % (i+1, j+1), "w") as f:
                    for k in xrange(leaf_num):
                        f.write(
                            "table_add int_mcast_table do_int_mcast %d => 1\n" % (k+1))
                    temp = 2
                    for k in xrange(leaf_num, leaf_num+h_num):
                        f.write(
                            "table_add int_mcast_table do_int_mcast %d => %d\n" % (k+1, temp))
                        temp += 1
                    f.write("\n")

                    f.write("mc_mgrp_create 1\n")
                    int_mcast_list = [
                        n+1 for n in xrange(leaf_num, leaf_num+h_num)]
                    int_mcast_list = tuple(int_mcast_list)
                    f.write("mc_node_create 0")
                    for m in int_mcast_list:
                        f.write(" %d" % m)
                    f.write("\n")
                    f.write("mc_node_associate 1 0\n")
                    f.write("\n")

                    temp = 2
                    for k in xrange(leaf_num, leaf_num+h_num):
                        f.write("mc_mgrp_create %d\n" % temp)
                        int_mcast_list = [n+1 for n in xrange(leaf_num+h_num)]
                        int_mcast_list.remove(k+1)
                        int_mcast_list = tuple(int_mcast_list)
                        f.write("mc_node_create %d" % (temp-1))
                        for m in int_mcast_list:
                            f.write(" %d" % m)
                        f.write("\n")
                        f.write("mc_node_associate %d %d\n" % (temp, temp-1))
                        f.write("\n")
                        temp += 1

                    f.write("table_add int_table do_int => %d\n" % sw_id)
                    sw_id += 1

                with open("dump_flow_table.sh", "a") as f:
                    f.write("sudo simple_switch_CLI --thrift-port %d <flow_table/p%d_t%d.txt\n" %
                            (thrift_port, i+1, j+1))
                    thrift_port += 1


if __name__ == "__main__":
    flow_table1 = flow_table()
    flow_table1.flow_table_gen([2, 2, 2, 2, 2])
