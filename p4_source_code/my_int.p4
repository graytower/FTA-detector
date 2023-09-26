/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_t {
    bit<48>   dstMac;
    bit<48>   srcMac;
}

header type_t {
    bit<16>   protocol;    // 0x700:sr; 0x701:int; 0x800:ipv4
}     

header sr_option_t {  
    bit<8>    flag;
    bit<8>    sr_num;
}

header sr_t {   
    bit<8>    flag;
    bit<8>    next_port;
}

header int_option_t {
    bit<8>    flag;    // ABCDEFG. A: 0-INT REQ, 1-INT ACK
    bit<8>    int_num;         
}

header inthdr_t {
    bit<16>   sw_id;
    bit<16>   ingress_port;
    bit<16>   egress_port;
    bit<16>   rsvd;
}

struct headers {
    ethernet_t      ethernet; 
    type_t[1]       type_1;
    sr_option_t[1]  sr_option;
    sr_t[10]        sr;
    type_t          type_2;
    int_option_t    int_option;
    inthdr_t        inthdr;
}

header sr_num_remain_md_t {
    bit<8>  sr_num_remain;
}


struct metadata {
    sr_num_remain_md_t sr_num_remain_md;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition parse_type_1;
    }

    state parse_type_1 {
        packet.extract(hdr.type_1[0]);
        transition select(hdr.type_1[0].protocol) {
            0x700: parse_sr_option;
            0x701: parse_int_option;
            default: accept;
        }
    }

    state parse_sr_option {
        packet.extract(hdr.sr_option[0]);
        meta.sr_num_remain_md.sr_num_remain = hdr.sr_option[0].sr_num;
        transition parse_sr;
    }

    state parse_sr {
        packet.extract(hdr.sr.next);
        meta.sr_num_remain_md.sr_num_remain = meta.sr_num_remain_md.sr_num_remain - 1;
        transition select(meta.sr_num_remain_md.sr_num_remain) {
            0: parse_type_2;
            default: parse_sr;
        }
    }

    state parse_type_2 {
        packet.extract(hdr.type_2);
        transition select(hdr.type_2.protocol) {
            0x701: parse_int_option;
            default: accept;
        }
    }

    state parse_int_option {
        packet.extract(hdr.int_option);
        transition accept;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action do_sr() {
        standard_metadata.egress_spec = (bit<9>)hdr.sr[0].next_port;
        hdr.sr.pop_front(1);
        hdr.sr_option[0].sr_num = hdr.sr_option[0].sr_num - 1;
    }

    action do_int_mcast(bit<16> mcast_grp) {
        standard_metadata.mcast_grp = mcast_grp;
    }

    table int_mcast_table {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            do_int_mcast;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }
    
    apply {
        if(hdr.sr_option[0].isValid()) {
            do_sr();
            if(hdr.sr_option[0].sr_num == 0) {
                hdr.type_1.pop_front(1);
                hdr.sr_option.pop_front(1);
            }
        }
        else if(hdr.int_option.isValid()){
            int_mcast_table.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {  
    action drop() {
        mark_to_drop(standard_metadata);
    }  

    action do_int(bit<16> sw_id) {
        hdr.inthdr.setValid();
        hdr.inthdr.sw_id = sw_id;
        hdr.inthdr.ingress_port=(bit<16>)standard_metadata.ingress_port;
        hdr.inthdr.egress_port=(bit<16>)standard_metadata.egress_port;
        hdr.int_option.int_num = hdr.int_option.int_num + 1;
    }

    table int_table {
        actions = {
            do_int;
            NoAction;
        }
        default_action = NoAction();
    }
    
    apply {
        if (hdr.int_option.isValid()) {
            // If INT REQ, flag: A=0
            if(hdr.int_option.flag < 0x80){
                int_table.apply();
            }
        }
        else {
            NoAction();
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {}
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.type_1);
        packet.emit(hdr.sr_option);
        packet.emit(hdr.sr);
        packet.emit(hdr.type_2);
        packet.emit(hdr.int_option);
        packet.emit(hdr.inthdr);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
