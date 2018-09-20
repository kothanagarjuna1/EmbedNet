#!/bin/bash
cd /home/lantronix/sdk/
tar -xvf xPico200-linux64_2.0.0.1R6.tar.gz
echo "build helloDemo"
cd custom/project/helloDemo
make
echo "build echoDemo"
cd ../echoDemo
make
echo "build powerDownDemo"
cd ../powerDownDemo
make
echo "build customDataDemo"
cd ../customDataDemo
make
echo "build configurablePinDemo"
cd ../configurablePinDemo
make
echo "build secureTunnelDemo"
cd ../secureTunnelDemo
make
echo "build tcpTunnelDemo"
cd ../tcpTunnelDemo
make
echo "build udpTunnelDemo"
cd ../udpTunnelDemo
make
echo "mach10SerialAPIDemo"
cd ../mach10SerialAPIDemo
make
echo "xmlAccessDemo"
cd ../xmlAccessDemo
make
echo "spiLogDemo"
cd ../spiLogDemo
make
echo "btOemProvisioningDemo"
cd ../btOemProvisioningDemo
make
echo "btHelloSensorDemo"
cd ../btHelloSensorDemo
make


echo "copy scripts to linux PC"
cd ../../../work/helloDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/echoDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF


cd ../../../work/powerDownDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF


cd ../../../work/xmlAccessDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/customDataDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/udpTunnelDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/tcpTunnelDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/configurablePinDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/secureTunnelDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/btHelloSensorDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/spiLogDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

cd ../../../work/btOemProvisioningDemo
ftp -inv 172.19.229.52 << EOF
user ltrxengr t35ting
mput *.rom
bye
EOF

