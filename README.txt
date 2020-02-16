Please refer to proj_sdn.pdf for detailed usage.

Open two consoles:
 $ ryu-manager --observe-links shortest_paths.py
 # python run_mininet.py <graph_type> [<parameter>]

In the second console, you can run commands like:

MN> link s1 s2 down
MN> link s1 h1 down
MN> pingall
MN> s1 ping s2