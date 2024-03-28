#!/bin/sh

TZ="${TZ:-Asia/Ho_Chi_Minh}"

rm -rf /etc/localtime
ln -s /usr/share/zoneinfo/$TZ /etc/localtime
echo $TZ > /etc/timezone

# Configure postfix
function setup_conf_and_secret {
    postconf -e "relayhost = [$MTP_RELAY]:$MTP_PORT"
    postconf -e "smtp_generic_maps = texthash:/etc/postfix/generic"
    postconf -e "smtp_sasl_mechanism_filter = plain, login, ntlm, gssapi "
    postconf -e 'smtp_sasl_auth_enable = yes'
    postconf -e 'smtpd_sasl_auth_enable = yes'
    postconf -e 'smtp_use_tls = yes'
    postconf -e 'smtp_sasl_password_maps = texthash:/etc/postfix/relay_passwd'
    # postconf -e 'sender_canonical_maps = hash:/etc/postfix/sender_canonical'
    postconf -e 'smtp_sasl_security_options = noanonymous'
    postconf -e 'smtp_sasl_tls_security_options = noanonymous'
    postconf -e 'mynetworks = 0.0.0.0/0'

    echo "[${MTP_RELAY}]:${MTP_PORT} ${MTP_USER}:${MTP_PASS}" > /etc/postfix/relay_passwd

cat <<EOF > /etc/postfix/generic
icinga ${MTP_USER}
root ${MTP_USER}
juniper ${MTP_USER}
rundeck ${MTP_USER}
EOF

    postmap /etc/postfix/relay_passwd
    postmap /etc/postfix/generic
    newaliases
    postmap /etc/postfix/aliases
}

if [ -z "$MTP_INTERFACES" ]; then
  postconf -e "inet_interfaces = all"
else
  postconf -e "inet_interfaces = $MTP_INTERFACES"
fi

if [ ! -z "$MTP_HOST" ]; then
  postconf -e "myhostname = $MTP_HOST"
fi

if [ ! -z "$MTP_DESTINATION" ]; then
  postconf -e "mydestination = $MTP_DESTINATION"
fi

if [ ! -z "$MTP_BANNER" ]; then
  postconf -e "smtpd_banner = $MTP_BANNER"
fi

if [ ! -z "$MTP_RELAY_DOMAINS" ]; then
  postconf -e "relay_domains = $MTP_RELAY_DOMAINS"
fi

if [ ! -z "$MAIL_LOG_FILE" ]; then
  postconf maillog_file=$MAIL_LOG_FILE
fi

if [ ! -z "$MTP_MESSAGE_SIZE_LIMIT" ]; then
  postconf -e "message_size_limit = ${MTP_MESSAGE_SIZE_LIMIT}"
fi

if [ ! -z "$MTP_MESSAGE_SIZE_LIMIT" ]; then
  postconf -e "mailbox_size_limit = ${MTP_MAILBOX_SIZE_LIMIT}"
fi

if [ ! -z "$MTP_RELAY" -a ! -z "$MTP_PORT" -a ! -z "$MTP_USER" -a ! -z "$MTP_PASS" ]; then
    setup_conf_and_secret
else
    postconf -e 'mynetworks = 127.0.0.1/32 192.168.0.0/16 172.16.0.0/12 172.17.0.0/16 10.0.0.0/8'
fi

if [ $(grep -c "^#header_checks" /etc/postfix/main.cf) -eq 1 ]; then
	sed -i 's/#header_checks/header_checks/' /etc/postfix/main.cf
        echo "/^Subject:/     WARN" >> /etc/postfix/header_checks
        postmap /etc/postfix/header_checks
fi

exec /usr/sbin/postfix start-fg