#include <iostream>

#include <hiredis/hiredis.h>

#include "MyRawSocket.h"
#include "MyProtocol.h"

using namespace std;

int main()
{
    // Create a raw socket
    MyRawSocket my_raw_socket((unsigned char *)"eth0");
    unsigned char local_mac[6];
    my_raw_socket.GetMac(local_mac);

    // Import protocol
    MyProtocol my_protocol;

    // Initiate the receive buffer
    int mtu = 1500;
    unsigned char send_buffer[mtu] = {0};
    unsigned char recv_buffer[mtu] = {0};

    // Create redis connection
    redisContext *c = redisConnectUnix("/var/run/redis/redis-server.sock");
    redisReply *r;

    // Start receiving
    while (true)
    {
        int recv_packet_length = my_raw_socket.RecvPacket(recv_buffer, sizeof(recv_buffer));

        int send_index = 0;
        int recv_index = 0;

        // Filter: Length > 14 (has Ethernet)
        if (recv_packet_length < 14)
        {
            continue;
        }

        // Parser: H_ETHERNET
        struct H_ETHERNET recv_ethernet = my_protocol.GetEthernet(recv_buffer, recv_index);
        recv_index += sizeof(recv_ethernet);

        // Filter: Get packets which are not sent from local
        if (local_mac[0] == recv_ethernet.src_mac[0] && local_mac[1] == recv_ethernet.src_mac[1] &&
            local_mac[2] == recv_ethernet.src_mac[2] && local_mac[3] == recv_ethernet.src_mac[3] &&
            local_mac[4] == recv_ethernet.src_mac[4] && local_mac[5] == recv_ethernet.src_mac[5])
        {
            continue;
        }

        // Parser: H_TYPE
        struct H_TYPE recv_type = my_protocol.GetType(recv_buffer, recv_index);
        recv_index += sizeof(recv_type);

        // Action: INT probe (0x0701)
        if (recv_type.protocol[0] == (unsigned char)0x07 && recv_type.protocol[1] == (unsigned char)0x01)
        {
            // Parser: H_INT_OPTION
            struct H_INT_OPTION recv_int_option = my_protocol.GetIntOption(recv_buffer, recv_index);
            recv_index += sizeof(recv_int_option);

            // Parser: H_INT_INFO
            int recv_int_option_int_num = recv_int_option.int_num[0];
            struct H_INT_INFO recv_int_info[recv_int_option_int_num] = {};
            for (int i = 0; i < recv_int_option_int_num; i++)
            {
                recv_int_info[i] = my_protocol.GetIntInfo(recv_buffer, recv_index);
                recv_index += sizeof(recv_int_info[i]);
            }

            // If INT REQ, send ACK
            if (recv_int_option.flag[0] < (unsigned char)0x80)
            {
                // Set: H_ETHERNET
                send_index = my_protocol.SetEthernet(send_buffer, send_index,
                                                     recv_ethernet.src_mac, sizeof(recv_ethernet.src_mac),
                                                     local_mac, sizeof(local_mac));

                // Set: H_TYPE (SR)
                unsigned char send_type_protocol_sr[2] = {0x07, 0x00};
                send_index = my_protocol.SetType(send_buffer, send_index,
                                                 send_type_protocol_sr, sizeof(send_type_protocol_sr));

                // Set: H_SR_OPTION
                unsigned char send_sr_option_flag[1] = {0x00};
                unsigned char send_sr_option_sr_num[1] = {recv_int_option.int_num[0]};
                send_index = my_protocol.SetSrOption(send_buffer, send_index,
                                                     send_sr_option_flag, sizeof(send_sr_option_flag),
                                                     send_sr_option_sr_num, sizeof(send_sr_option_sr_num));

                // Set: H_SR
                for (int i = 0; i < recv_int_option_int_num; i++)
                {
                    unsigned char send_sr_flag[1] = {0x00};
                    unsigned char send_sr_next_port[1] = {recv_int_info[i].ingress_port[1]};
                    send_index = my_protocol.SetSr(send_buffer, send_index,
                                                   send_sr_flag, sizeof(send_sr_flag),
                                                   send_sr_next_port, sizeof(send_sr_next_port));
                }

                // Set: H_TYPE (INT)
                unsigned char send_type_protocol_int[2] = {0x07, 0x01};
                send_index = my_protocol.SetType(send_buffer, send_index,
                                                 send_type_protocol_int, sizeof(send_type_protocol_int));

                // Set: H_INT_Option
                unsigned char send_int_option_flag[1] = {0x80};
                unsigned char send_int_option_int_num[1] = {recv_int_option.int_num[0]};
                send_index = my_protocol.SetIntOption(send_buffer, send_index,
                                                      send_int_option_flag, sizeof(send_int_option_flag),
                                                      send_int_option_int_num, sizeof(send_int_option_int_num));

                // Set: INT (reversed)
                for (int i = recv_int_option_int_num - 1; i >= 0; i--)
                {
                    send_index = my_protocol.SetIntInfo(send_buffer, send_index,
                                                        recv_int_info[i].sw_id, sizeof(recv_int_info[i].sw_id),
                                                        recv_int_info[i].ingress_port, sizeof(recv_int_info[i].ingress_port),
                                                        recv_int_info[i].egress_port, sizeof(recv_int_info[i].egress_port),
                                                        recv_int_info[i].rsvd, sizeof(recv_int_info[i].rsvd));
                }

                // Send
                my_raw_socket.SendPacket(send_buffer, send_index);
            }

            // If INT ACK, store
            else
            {
                char key[128] = {0};
                int key_index = 0;

                char value[128] = {0};
                int value_index = 0;

                // Set src mac and dst mac for key
                key_index += sprintf(key + key_index, "%02x:%02x:%02x:%02x:%02x:%02x--%02x:%02x:%02x:%02x:%02x:%02x--",
                                     local_mac[0], local_mac[1],
                                     local_mac[2], local_mac[3],
                                     local_mac[4], local_mac[5],
                                     recv_ethernet.src_mac[0], recv_ethernet.src_mac[1],
                                     recv_ethernet.src_mac[2], recv_ethernet.src_mac[3],
                                     recv_ethernet.src_mac[4], recv_ethernet.src_mac[5]);

                // Set key and value
                for (int i = 0; i < recv_int_option_int_num; i++)
                {
                    int sw_id = (recv_int_info[i].sw_id[0] << 8) + recv_int_info[i].sw_id[1];
                    int ingress_port = (recv_int_info[i].ingress_port[0] << 8) + recv_int_info[i].ingress_port[1];
                    int egress_port = (recv_int_info[i].egress_port[0] << 8) + recv_int_info[i].egress_port[1];

                    if (i != recv_int_option_int_num - 1)
                    {
                        key_index += sprintf(key + key_index, "sw%d_%d--sw%d_%d--", sw_id, ingress_port, sw_id, egress_port);
                        value_index += sprintf(value + value_index, "%d--", egress_port);
                    }
                    else
                    {
                        key_index += sprintf(key + key_index, "sw%d_%d--sw%d_%d", sw_id, ingress_port, sw_id, egress_port);
                        value_index += sprintf(value + value_index, "%d", egress_port);
                    }
                }

                // Store path
                int time_out = 5;
                redisCommand(c, "setnx %s %s", key, value);
                redisCommand(c, "expire %s %d", key, time_out);

                cout << key << " " << value << " " << endl;
            }
        }
    }
}