#!/usr/bin/expect

# set timeout 3
spawn ./install.sh -s icinga

expect "Do you want to proceed?"
send -- "y\r"

expect "Please enter the path to the icinga base directory"
send -- "/etc/icinga2\r"

expect "Please enter the path to NagVis base"
send -- "/usr/share/nagvis\r"

expect "Do you want to update the backend configuration?"
send -- "n\r"

expect "Please enter the web path to NagVis"
send -- "/etc/apache2/conf-available\r"
# send -- "/nagvis\r"

expect "Please enter the name of the web-server user"
# send -- "apache\r"
send -- "www-data\r"

expect "Please enter the name of the web-server group"
# send -- "apache\r"
send -- "www-data\r"

expect "create Apache config file"
send -- "y\r"

expect "Do you want the installer to update your config files when possible"
send -- "y\r"

expect "Remove backup directory after successful installation"
send -- "y\r"

expect "Do you really want to continue"
send -- "y\r"

expect eof
