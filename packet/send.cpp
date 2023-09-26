#include <iostream>

#include "MyRawSocket.h"
#include "MyProtocol.h"

using namespace std;

int main()
{
    // Create a raw socket
    MyRawSocket my_raw_socket((unsigned char *)"eth0");

    // Import protocol
    MyProtocol my_protocol;

    // Initiate the send buffer
    int mtu = 1500;
    unsigned char send_buffer[mtu] = {0};
    int send_index = 0;

    // Set: H_ETHERNET
    unsigned char send_ethernet_dst_mac[6] = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
    unsigned char send_ethernet_src_mac[6] = {0};
    my_raw_socket.GetMac(send_ethernet_src_mac);
    send_index = my_protocol.SetEthernet(send_buffer, send_index,
                                         send_ethernet_dst_mac, sizeof(send_ethernet_dst_mac),
                                         send_ethernet_src_mac, sizeof(send_ethernet_src_mac));

    // Set: H_TYPE (INT)
    unsigned char send_type_protocol_int[2] = {0x07, 0x01};
    send_index = my_protocol.SetType(send_buffer, send_index,
                                     send_type_protocol_int, sizeof(send_type_protocol_int));

    // Set: H_INT_OPTION
    unsigned char send_int_option_flag[1] = {0x00};
    unsigned char send_int_option_int_num[1] = {0x00};
    send_index = my_protocol.SetIntOption(send_buffer, send_index,
                                          send_int_option_flag, sizeof(send_int_option_flag),
                                          send_int_option_int_num, sizeof(send_int_option_int_num));

    // Send
    while (true)
    {
        my_raw_socket.SendPacket(send_buffer, send_index);
        sleep(1);
    }
}