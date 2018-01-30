: ${ROOTPW:=root}
echo 'root:'${ROOTPW} |chpasswd
: ${XROS_USER:=xrosfs}
: ${XROS_USERPW:=xrosfs}

# Add user
useradd -d /home/${XROS_USER} -g users -u 1000 -m -s /bin/bash ${XROS_USER}
# RUN echo ${XROS_USER}:${XROS_USERPW} |chpasswd
echo ${XROS_USER}:${XROS_USERPW} |chpasswd

# generate ssh host keys
if ls /etc/ssh/ssh_host_* 1> /dev/null 2>&1; then
  :
else
  ssh-keygen -A
fi

# tweak autofs config
sed -e 's/^timeout = 300/timeout = '"$AUTOFS_TIMEOUT"'/' -i /etc/autofs.conf


IPADDR="$(hostname -i)"

/usr/bin/supervisord -n -c "/etc/supervisor/supervisord.conf" &

RET=0
while [ ${RET} -ne 4 ] ; do
  RET=$(supervisorctl status | grep -i running | wc -l)
done

/bin/sleep 5
cat <<EOF

#    # #####   ####   ####      ####  #    # ###### #####  
 #  #  #    # #    # #         #    # #    # #      #    # 
  ##   #    # #    #  ####     #    # #    # #####  #    # 
  ##   #####  #    #      #    #    # #    # #      #####  
 #  #  #   #  #    # #    #    #    #  #  #  #      #   #  
#    # #    #  ####   ####      ####    ##   ###### #    # 

                         ####   ####  #    # ######  ####  
                        #      #      #    # #      #      
                         ####   ####  ###### #####   ####  
                             #      # #    # #           # 
                        #    # #    # #    # #      #    # 
                         ####   ####  #    # #       ####  
                                   
EOF

echo '----'
source /usr/local/bin/xros_tldr
echo '----'
echo ''
# /bin/sleep 30

unset ROOTPW  # How do I unset env from system global ?
unset XROS_USER
unset XROS_USERPW

/usr/bin/supervisorctl tail -f log_event_listener stderr
