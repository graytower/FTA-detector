#ifndef MYSENDRAWPACKET_H
#define MYSENDRAWPACKET_H

#include <iostream>
#include <net/ethernet.h>    // ETH_P_ALL
#include <linux/if_packet.h> // sockaddr_ll
#include <string.h>          // strncpy
#include <sys/socket.h>      // socket
#include <sys/ioctl.h>       // ioctl
#include <net/if.h>          // ifreq
#include <unistd.h>          // close
#include <arpa/inet.h>       // hton

#include "MyProtocol.h"

using namespace std;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Use raw socket to send or receive customized packets. The related headers and protocols are contained in MyProtocol.h (or something like this)
// Emample:
//     unsigned char *test = new unsigned char[1500]; // Create a send buffer
//     MyRawSocket myrawsocket((unsigned char *)"ens38"); // Create a raw socket
//     test[0] = 0x00; test[1] = 0x11; test[2] = 0x22; test[3] = 0x33; test[4] = 0x44; // Set send buffer
//     myrawsocket.SendPacket(test, 1500); // Send, input send buffer and packet length
//     delete[] test; // Release
class MyRawSocket
{
public:
    // Create socket connection
    MyRawSocket(const unsigned char *network_interface);

    // Get explicit MAC address
    void GetMac(unsigned char *local_mac);

    // Send and receive (recv)
    void SendPacket(const unsigned char *send_buffer, int send_packet_length);
    int RecvPacket(unsigned char *recv_buffer, int recv_buffer_length);

private:
    int raw_socket_fd_ = 0;
    unsigned char local_mac_[6] = {0};
    struct sockaddr_ll device_ = {};
};

// Input network_interface, like "eth0". Obtain the MAC address of this interface and create a raw socket for this device
MyRawSocket::MyRawSocket(const unsigned char *network_interface)
{
    // Create a raw socket to capture the MAC address
    int raw_socket_fd_for_local_mac = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    struct ifreq ifr = {};
    strncpy(ifr.ifr_name, (char *)network_interface, IFNAMSIZ - 1);
    ioctl(raw_socket_fd_for_local_mac, SIOCGIFHWADDR, &ifr);
    close(raw_socket_fd_for_local_mac);

    // Set devide infomation and fill in the related array and struct by MAC
    device_.sll_ifindex = if_nametoindex((char *)network_interface);
    device_.sll_family = AF_PACKET;
    for (int i = 0; i < 6; i++)
    {
        local_mac_[i] = ((unsigned char *)ifr.ifr_hwaddr.sa_data)[i];
        device_.sll_addr[i] = ((unsigned char *)ifr.ifr_hwaddr.sa_data)[i];
    }
    device_.sll_halen = htons(6);

    // Create raw socket for sending and receiving
    raw_socket_fd_ = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
}

// Obtain the MAC address if needed
void MyRawSocket::GetMac(unsigned char *local_mac)
{
    for (int i = 0; i < 6; i++)
    {
        local_mac[i] = local_mac_[i];
    }
}

// Send packet
void MyRawSocket::SendPacket(const unsigned char *send_buffer, int send_packet_length)
{
    sendto(raw_socket_fd_, send_buffer, send_packet_length, 0, (struct sockaddr *)&device_, sizeof(device_));
}

// Receive packet, store the packet into recv_buffer and return the length of the packet
int MyRawSocket::RecvPacket(unsigned char *recv_buffer, int recv_buffer_length)
{
    socklen_t address_length = sizeof(device_);

    int recv_packet_length = recvfrom(raw_socket_fd_, recv_buffer, recv_buffer_length, 0, (struct sockaddr *)&device_, &address_length);

    return recv_packet_length;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// int main()
// {
//     MyRawSocket myrawsocket((unsigned char *)"ens38");
//     unsigned char src_mac[6] = {0};
//     myrawsocket.GetMac(src_mac);

//     MyProtocol myprotocol;

//     unsigned char *buffer = new unsigned char[1500];
//     int index = 0;
//     unsigned char dst_mac[6] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66};
//     index = myprotocol.SetEthernet(buffer, index, dst_mac, sizeof(dst_mac), src_mac, sizeof(src_mac));

//     unsigned char type_1[2] = {0x07, 0x01};
//     index = myprotocol.SetType(buffer, index, type_1, sizeof(type_1));

//     cout << index << endl;

//     myrawsocket.SendPacket(buffer, 1500);

//     delete[] buffer;
// }

#endif