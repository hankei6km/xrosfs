# generate ssh host keys
if ls /etc/ssh/ssh_host_* 1> /dev/null 2>&1; then
  :
else
  ssh-keygen -A
fi

# start sshd server
/usr/sbin/sshd -D
