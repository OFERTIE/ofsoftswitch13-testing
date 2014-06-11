Tutorial 2: Basic IPv6 Experiments
==================================

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=2,eth\_type=0x86dd,ipv6\_src=fd10:0:0::2/48 meter:1 apply:output=1

> s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd,ipv6\_dst=fd10:0:0::1/48 meter:1 apply:output=2

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x800,ip\_proto=6 meter:1 apply:output=2

> s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd,ip\_proto=17 meter:1 apply:output=2

> s1 dpctl unix:/tmp/s1 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x800,ip\_dscp=8 meter:1 apply:output=2

> s2 dpctl unix:/tmp/s2 flow-mod cmd=add,table=0 in\_port=1,eth\_type=0x86dd,ipv6\_flabel=23 meter:1 apply:output=2


