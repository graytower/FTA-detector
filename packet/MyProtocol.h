#ifndef MYPROTOCOL_H
#define MYPROTOCOL_H

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Header define

struct H_ETHERNET
{
    unsigned char dst_mac[6];
    unsigned char src_mac[6];
};

struct H_TYPE
{
    unsigned char protocol[2];
};

struct H_SR_OPTION
{
    unsigned char flag[1]; // ABCDEFGH
    unsigned char sr_num[1];
};

struct H_SR
{
    unsigned char flag[1]; // ABCDEFGH
    unsigned char next_port[1];
};

struct H_INT_OPTION
{
    unsigned char flag[1]; // ABCDEFGH. A: 0-INT REQ, 1- INT ACK
    unsigned char int_num[1];
};

struct H_INT_INFO
{
    unsigned char sw_id[2];
    unsigned char ingress_port[2];
    unsigned char egress_port[2];
    unsigned char rsvd[2];
};

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class MyProtocol
{
public:
    int SetEthernet(unsigned char *buffer, int index,
                    const unsigned char *dst_mac, int dst_mac_length,
                    const unsigned char *src_mac, int src_mac_length);
    int SetType(unsigned char *buffer, int index,
                const unsigned char *protocol, int protocol_length);
    int SetSrOption(unsigned char *buffer, int index,
                    const unsigned char *flag, int flag_length,
                    const unsigned char *sr_num, int sr_num_length);
    int SetSr(unsigned char *buffer, int index,
              const unsigned char *flag, int flag_length,
              const unsigned char *next_port, int next_port_length);
    int SetIntOption(unsigned char *buffer, int index,
                     const unsigned char *flag, int flag_length,
                     const unsigned char *int_num, int int_num_length);
    int SetIntInfo(unsigned char *buffer, int index,
                   const unsigned char *sw_id, int sw_id_length,
                   const unsigned char *ingress_port, int ingress_port_length,
                   const unsigned char *egress_port, int egress_port_length,
                   const unsigned char *rsvd, int rsvd_length);

    struct H_ETHERNET GetEthernet(unsigned char *buffer, int index);
    struct H_TYPE GetType(unsigned char *buffer, int index);
    struct H_INT_OPTION GetIntOption(unsigned char *buffer, int index);
    struct H_INT_INFO GetIntInfo(unsigned char *buffer, int index);
};

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

int MyProtocol::SetEthernet(unsigned char *buffer, int index,
                            const unsigned char *dst_mac, int dst_mac_length,
                            const unsigned char *src_mac, int src_mac_length)
{
    for (int i = 0; i < dst_mac_length; i++)
    {
        buffer[index++] = dst_mac[i];
    }

    for (int i = 0; i < src_mac_length; i++)
    {
        buffer[index++] = src_mac[i];
    }

    return index;
}

int MyProtocol::SetType(unsigned char *buffer, int index,
                        const unsigned char *protocol, int protocol_length)
{
    for (int i = 0; i < protocol_length; i++)
    {
        buffer[index++] = protocol[i];
    }

    return index;
}

int MyProtocol::SetSrOption(unsigned char *buffer, int index,
                            const unsigned char *flag, int flag_length,
                            const unsigned char *sr_num, int sr_num_length)
{
    for (int i = 0; i < flag_length; i++)
    {
        buffer[index++] = flag[i];
    }

    for (int i = 0; i < sr_num_length; i++)
    {
        buffer[index++] = sr_num[i];
    }

    return index;
}

int MyProtocol::SetSr(unsigned char *buffer, int index,
                      const unsigned char *flag, int flag_length,
                      const unsigned char *next_port, int next_port_length)
{
    for (int i = 0; i < flag_length; i++)
    {
        buffer[index++] = flag[i];
    }

    for (int i = 0; i < next_port_length; i++)
    {
        buffer[index++] = next_port[i];
    }

    return index;
}

int MyProtocol::SetIntOption(unsigned char *buffer, int index,
                             const unsigned char *flag, int flag_length,
                             const unsigned char *int_num, int int_num_length)
{
    for (int i = 0; i < flag_length; i++)
    {
        buffer[index++] = flag[i];
    }

    for (int i = 0; i < int_num_length; i++)
    {
        buffer[index++] = int_num[i];
    }

    return index;
}

int MyProtocol::SetIntInfo(unsigned char *buffer, int index,
                           const unsigned char *sw_id, int sw_id_length,
                           const unsigned char *ingress_port, int ingress_port_length,
                           const unsigned char *egress_port, int egress_port_length,
                           const unsigned char *rsvd, int rsvd_length)
{
    for (int i = 0; i < sw_id_length; i++)
    {
        buffer[index++] = sw_id[i];
    }

    for (int i = 0; i < ingress_port_length; i++)
    {
        buffer[index++] = ingress_port[i];
    }

    for (int i = 0; i < egress_port_length; i++)
    {
        buffer[index++] = egress_port[i];
    }

    for (int i = 0; i < rsvd_length; i++)
    {
        buffer[index++] = rsvd[i];
    }

    return index;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

struct H_ETHERNET MyProtocol::GetEthernet(unsigned char *buffer, int index)
{
    struct H_ETHERNET ethernet = {};

    for (int i = 0; i < sizeof(ethernet.dst_mac); i++)
    {
        ethernet.dst_mac[i] = buffer[index++];
    }

    for (int i = 0; i < sizeof(ethernet.src_mac); i++)
    {
        ethernet.src_mac[i] = buffer[index++];
    }

    return ethernet;
}

struct H_TYPE MyProtocol::GetType(unsigned char *buffer, int index)
{
    struct H_TYPE type = {};

    for (int i = 0; i < sizeof(type.protocol); i++)
    {
        type.protocol[i] = buffer[index++];
    }

    return type;
}

struct H_INT_OPTION MyProtocol::GetIntOption(unsigned char *buffer, int index)
{
    struct H_INT_OPTION int_option = {};

    for (int i = 0; i < sizeof(int_option.flag); i++)
    {
        int_option.flag[i] = buffer[index++];
    }

    for (int i = 0; i < sizeof(int_option.int_num); i++)
    {
        int_option.int_num[i] = buffer[index++];
    }

    return int_option;
}

struct H_INT_INFO MyProtocol::GetIntInfo(unsigned char *buffer, int index)
{
    struct H_INT_INFO int_info = {};

    for (int i = 0; i < sizeof(int_info.sw_id); i++)
    {
        int_info.sw_id[i] = buffer[index++];
    }

    for (int i = 0; i < sizeof(int_info.ingress_port); i++)
    {
        int_info.ingress_port[i] = buffer[index++];
    }

    for (int i = 0; i < sizeof(int_info.egress_port); i++)
    {
        int_info.egress_port[i] = buffer[index++];
    }

    for (int i = 0; i < sizeof(int_info.rsvd); i++)
    {
        int_info.rsvd[i] = buffer[index++];
    }

    return int_info;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#endif
