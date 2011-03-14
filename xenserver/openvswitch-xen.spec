# Spec file for Open vSwitch.

# Copyright (C) 2009, 2010, 2011 Nicira Networks, Inc.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.

# When building, the rpmbuild command line should define
# openvswitch_version, xen_version, and build_number using -D arguments.
# for example:
#
#    rpmbuild -D "openvswitch_version 0.8.9~1+build123" -D "xen_version 2.6.18-128.1.1.el5.xs5.1.0.483.1000xen" -D "build_number --with-build-number=123" -bb /usr/src/redhat/SPECS/openvswitch-xen.spec

%define version %{openvswitch_version}-%{xen_version}

# bump this when breaking compatibility with userspace
%define module_abi_version 0

# extract kernel type (xen or kdump)
%define binsuffix -%(echo '%{xen_version}' | sed -r 's/^.*[0-9]+//')
# kernel version string w/o kernel type
%define kernel_version %(echo '%{xen_version}' | sed -r 's/[a-z]+$//')
# build-supplemental-pack.sh requires this naming for kernel module packages
%define module_package modules%{binsuffix}-%{kernel_version}

Name: openvswitch
Summary: Open vSwitch daemon/database/utilities
Group: System Environment/Daemons
URL: http://www.openvswitch.org/
Vendor: Nicira Networks, Inc.
Version: %{openvswitch_version}

License: ASL 2.0
Release: 1
Source: openvswitch-%{openvswitch_version}.tar.gz
Buildroot: /tmp/openvswitch-xen-rpm
Requires: openvswitch_mod.ko.%{module_abi_version}

%description
Open vSwitch provides standard network bridging functions augmented with
support for the OpenFlow protocol for remote per-flow control of
traffic.

%package %{module_package}
Summary: Open vSwitch kernel module
Group: System Environment/Kernel
License: GPLv2
Provides: %{name}-modules = %{kernel_version}, openvswitch_mod.ko.%{module_abi_version}
Requires: kernel%{binsuffix} = %{kernel_version}

%description %{module_package}
Open vSwitch Linux kernel module compiled against kernel version
%{xen_version}.

%prep
%setup -q -n openvswitch-%{openvswitch_version}

%build
./configure --prefix=/usr --sysconfdir=/etc --localstatedir=%{_localstatedir} --with-l26=/lib/modules/%{xen_version}/build --enable-ssl %{build_number}
make %{_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT/etc
install -d -m 755 $RPM_BUILD_ROOT/etc/init.d
install -m 755 xenserver/etc_init.d_openvswitch \
         $RPM_BUILD_ROOT/etc/init.d/openvswitch
install -m 755 xenserver/etc_init.d_openvswitch-xapi-update \
         $RPM_BUILD_ROOT/etc/init.d/openvswitch-xapi-update
install -d -m 755 $RPM_BUILD_ROOT/etc/sysconfig
install -d -m 755 $RPM_BUILD_ROOT/etc/logrotate.d
install -m 755 xenserver/etc_logrotate.d_openvswitch \
         $RPM_BUILD_ROOT/etc/logrotate.d/openvswitch
install -d -m 755 $RPM_BUILD_ROOT/etc/profile.d
install -m 755 xenserver/etc_profile.d_openvswitch.sh \
         $RPM_BUILD_ROOT/etc/profile.d/openvswitch.sh
install -d -m 755 $RPM_BUILD_ROOT/etc/xapi.d/plugins
install -m 755 xenserver/etc_xapi.d_plugins_openvswitch-cfg-update \
         $RPM_BUILD_ROOT/etc/xapi.d/plugins/openvswitch-cfg-update
install -d -m 755 $RPM_BUILD_ROOT/etc/xensource/bugtool/network-status
install -m 644 xenserver/etc_xensource_bugtool_network-status_openvswitch.xml \
         $RPM_BUILD_ROOT/etc/xensource/bugtool/network-status/openvswitch.xml
install -d -m 755 $RPM_BUILD_ROOT/usr/share/openvswitch/scripts
install -m 644 vswitchd/vswitch.ovsschema \
         $RPM_BUILD_ROOT/usr/share/openvswitch/vswitch.ovsschema
install -m 755 xenserver/opt_xensource_libexec_interface-reconfigure \
             $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/interface-reconfigure
install -m 644 xenserver/opt_xensource_libexec_InterfaceReconfigure.py \
             $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/InterfaceReconfigure.py
install -m 644 xenserver/opt_xensource_libexec_InterfaceReconfigureBridge.py \
             $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/InterfaceReconfigureBridge.py
install -m 644 xenserver/opt_xensource_libexec_InterfaceReconfigureVswitch.py \
             $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/InterfaceReconfigureVswitch.py
install -m 755 xenserver/etc_xensource_scripts_vif \
             $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/vif
install -m 755 xenserver/usr_share_openvswitch_scripts_ovs-xapi-sync \
               $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovs-xapi-sync
install -m 755 xenserver/usr_share_openvswitch_scripts_sysconfig.template \
         $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/sysconfig.template
install -m 755 xenserver/usr_share_openvswitch_scripts_xen-bugtool-tc-class-show \
         $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/xen-bugtool-tc-class-show
install -m 755 utilities/ovs-save \
         $RPM_BUILD_ROOT/usr/share/openvswitch/scripts/ovs-save
install -d -m 755 $RPM_BUILD_ROOT/usr/lib/xsconsole/plugins-base
install -m 644 \
        xenserver/usr_lib_xsconsole_plugins-base_XSFeatureVSwitch.py \
               $RPM_BUILD_ROOT/usr/lib/xsconsole/plugins-base/XSFeatureVSwitch.py

install -d -m 755 $RPM_BUILD_ROOT/lib/modules/%{xen_version}/kernel/extra/openvswitch
find datapath/linux-2.6 -name *.ko -exec install -m 755  \{\} $RPM_BUILD_ROOT/lib/modules/%{xen_version}/kernel/extra/openvswitch \;
install xenserver/uuid.py $RPM_BUILD_ROOT/usr/share/openvswitch/python

# Get rid of stuff we don't want to make RPM happy.
rm \
    $RPM_BUILD_ROOT/usr/bin/ovs-controller \
    $RPM_BUILD_ROOT/usr/bin/ovs-discover \
    $RPM_BUILD_ROOT/usr/bin/ovs-openflowd \
    $RPM_BUILD_ROOT/usr/bin/ovs-pki \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-controller.8 \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-discover.8 \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-openflowd.8 \
    $RPM_BUILD_ROOT/usr/share/man/man8/ovs-pki.8

install -d -m 755 $RPM_BUILD_ROOT/var/lib/openvswitch

%clean
rm -rf $RPM_BUILD_ROOT

%post
if grep -F net.ipv4.conf.all.arp_filter /etc/sysctl.conf >/dev/null 2>&1; then :; else
    cat >>/etc/sysctl.conf <<EOF
# This works around an issue in xhad, which binds to a particular
# Ethernet device, which in turn causes ICMP port unreachable messages
# if packets are received are on the wrong interface, which in turn
# can happen if we send out ARP replies on every interface (as Linux
# does by default) instead of just on the interface that has the IP
# address being ARPed for, which this sysctl setting in turn works
# around.
#
# Bug #1378.
net.ipv4.conf.all.arp_filter = 1
EOF
fi

if test ! -e /etc/openvswitch/conf.db; then
    install -d -m 755 -o root -g root /etc/openvswitch

    # Create ovs-vswitchd config database
    ovsdb-tool -vANY:console:emer create /etc/openvswitch/conf.db \
            /usr/share/openvswitch/vswitch.ovsschema

    # Create initial table in config database
    ovsdb-tool -vANY:console:emer transact /etc/openvswitch/conf.db \
            '[{"op": "insert", "table": "Open_vSwitch", "row": {}}]' \
            > /dev/null
fi

# Create default or update existing /etc/sysconfig/openvswitch.
SYSCONFIG=/etc/sysconfig/openvswitch
TEMPLATE=/usr/share/openvswitch/scripts/sysconfig.template
if [ ! -e $SYSCONFIG ]; then
    cp $TEMPLATE $SYSCONFIG
else
    for var in $(awk -F'[ :]' '/^# [_A-Z0-9]+:/{print $2}' $TEMPLATE)
    do
        if ! grep $var $SYSCONFIG >/dev/null 2>&1; then
            echo >> $SYSCONFIG
            sed -n "/$var:/,/$var=/p" $TEMPLATE >> $SYSCONFIG
        fi
    done
fi

# Deliberately break %postun in broken OVS builds that revert original
# XenServer scripts during rpm -U by moving the directory where it thinks
# they are saved.
if [ -d /usr/lib/openvswitch/xs-original ]; then
    mkdir -p /usr/lib/openvswitch/xs-saved
    mv /usr/lib/openvswitch/xs-original/* /usr/lib/openvswitch/xs-saved/ &&
        rmdir /usr/lib/openvswitch/xs-original
fi

# Replace XenServer files by our versions.
mkdir -p /usr/lib/openvswitch/xs-saved \
    || printf "Could not create script backup directory.\n"
for f in \
    /opt/xensource/libexec/interface-reconfigure \
    /opt/xensource/libexec/InterfaceReconfigure.py \
    /opt/xensource/libexec/InterfaceReconfigureBridge.py \
    /opt/xensource/libexec/InterfaceReconfigureVswitch.py \
    /etc/xensource/scripts/vif
do
    s=$(basename "$f")
    t=$(readlink "$f")
    if [ -f "$f" ] && [ "$t" != "/usr/share/openvswitch/scripts/$s" ]; then
        mv "$f" /usr/lib/openvswitch/xs-saved/ \
            || printf "Could not save original XenServer $s script\n"
        ln -s "/usr/share/openvswitch/scripts/$s" "$f" \
            || printf "Could not link to Open vSwitch $s script\n"
    fi
done

# Clean up dangling symlinks to removed OVS replacement scripts no longer
# provided by OVS. Any time a replacement script is removed from OVS,
# it should be added here to ensure correct reversion from old versions of
# OVS that don't clean up dangling symlinks during the uninstall phase.
for orig in \
    /usr/sbin/brctl \
    /usr/sbin/xen-bugtool
do
    saved=/usr/lib/openvswitch/xs-saved/$(basename "$orig")
    [ -e "$saved" ] && mv -f "$saved" "$orig"
done

# Ensure all required services are set to run
for s in openvswitch openvswitch-xapi-update; do
    if chkconfig --list $s >/dev/null 2>&1; then
        chkconfig --del $s || printf "Could not remove $s init script."
    fi
    chkconfig --add $s || printf "Could not add $s init script."
    chkconfig $s on || printf "Could not enable $s init script."
done

if [ "$1" = "1" ]; then    # $1 = 2 for upgrade
    # Configure system to use Open vSwitch
    echo vswitch > /etc/xensource/network.conf

    printf "\nYou MUST reboot the server NOW to complete the change to\n"
    printf "Open vSwitch.  Attempts to modify networking on the server\n"
    printf "or any hosted VM will fail until after the reboot and could\n"
    printf "leave the server in an state requiring manual recovery.\n\n"
else
    printf "\nTo use the new Open vSwitch install, you should reboot the\n" 
    printf "server now.  Failure to do so may result in incorrect operation."
    printf "\n\n"
fi

%post %{module_package}
# Ensure that modprobe will find our modules.
depmod %{xen_version}

%preun
if [ "$1" = "0" ]; then     # $1 = 1 for upgrade
    for s in openvswitch openvswitch-xapi-update; do
        chkconfig --del $s || printf "Could not remove $s init script."
    done
fi

%postun
# Restore original XenServer scripts if the OVS equivalent no longer exists.
# This works both in the upgrade and erase cases.
# This lists every file that every version of OVS has ever replaced. Never
# remove old files that OVS no longer replaces, or upgrades from old versions
# will fail to restore the XS originals, leaving the system in a broken state.
# Also be sure to add removed script paths to the %post scriptlet above to
# prevent the same problem when upgrading from old versions of OVS that lack
# this restore-on-upgrade logic.
for f in \
    /etc/xensource/scripts/vif \
    /usr/sbin/brctl \
    /usr/sbin/xen-bugtool \
    /opt/xensource/libexec/interface-reconfigure \
    /opt/xensource/libexec/InterfaceReconfigure.py \
    /opt/xensource/libexec/InterfaceReconfigureBridge.py \
    /opt/xensource/libexec/InterfaceReconfigureVswitch.py
do
    # Only revert dangling symlinks.
    if [ -h "$f" ] && [ ! -e "$f" ]; then
        s=$(basename "$f")
        if [ ! -f "/usr/lib/openvswitch/xs-saved/$s" ]; then
            printf "Original XenServer $s script not present in /usr/lib/openvswitch/xs-saved\n" >&2
            printf "Could not restore original XenServer script.\n" >&2
        else
            (rm -f "$f" \
                && mv "/usr/lib/openvswitch/xs-saved/$s" "$f") \
                || printf "Could not restore original XenServer $s script.\n" >&2
        fi
    fi
done

if [ "$1" = "0" ]; then     # $1 = 1 for upgrade
    rm -f /usr/lib/xsconsole/plugins-base/XSFeatureVSwitch.pyc \
        /usr/lib/xsconsole/plugins-base/XSFeatureVSwitch.pyo

    rm -f /usr/share/openvswitch/scripts/InterfaceReconfigure.pyc \
        /usr/share/openvswitch/scripts/InterfaceReconfigure.pyo \
        /usr/share/openvswitch/scripts/InterfaceReconfigureBridge.pyc \
        /usr/share/openvswitch/scripts/InterfaceReconfigureBridge.pyo \
        /usr/share/openvswitch/scripts/InterfaceReconfigureVSwitch.pyc \
        /usr/share/openvswitch/scripts/InterfaceReconfigureVSwitch.pyo

    # Remove all configuration files
    rm -f /etc/openvswitch/conf.db
    rm -f /etc/sysconfig/openvswitch
    rm -f /etc/openvswitch/vswitchd.cacert
    rm -f /var/xapi/network.dbcache

    # Remove saved XenServer scripts directory, but only if it's empty
    rmdir -p /usr/lib/openvswitch/xs-saved 2>/dev/null

    # Configure system to use bridge
    echo bridge > /etc/xensource/network.conf

    printf "\nYou MUST reboot the server now to complete the change to\n"
    printf "standard Xen networking.  Attempts to modify networking on the\n"
    printf "server or any hosted VM will fail until after the reboot and\n"
    printf "could leave the server in a state requiring manual recovery.\n\n"
fi

%files
%defattr(-,root,root)
/etc/init.d/openvswitch
/etc/init.d/openvswitch-xapi-update
/etc/xapi.d/plugins/openvswitch-cfg-update
/etc/xensource/bugtool/network-status/openvswitch.xml
/etc/logrotate.d/openvswitch
/etc/profile.d/openvswitch.sh
/usr/share/openvswitch/python/ovs/__init__.py
/usr/share/openvswitch/python/ovs/daemon.py
/usr/share/openvswitch/python/ovs/db/__init__.py
/usr/share/openvswitch/python/ovs/db/data.py
/usr/share/openvswitch/python/ovs/db/error.py
/usr/share/openvswitch/python/ovs/db/idl.py
/usr/share/openvswitch/python/ovs/db/parser.py
/usr/share/openvswitch/python/ovs/db/schema.py
/usr/share/openvswitch/python/ovs/db/types.py
/usr/share/openvswitch/python/ovs/dirs.py
/usr/share/openvswitch/python/ovs/fatal_signal.py
/usr/share/openvswitch/python/ovs/json.py
/usr/share/openvswitch/python/ovs/jsonrpc.py
/usr/share/openvswitch/python/ovs/ovsuuid.py
/usr/share/openvswitch/python/ovs/poller.py
/usr/share/openvswitch/python/ovs/process.py
/usr/share/openvswitch/python/ovs/reconnect.py
/usr/share/openvswitch/python/ovs/socket_util.py
/usr/share/openvswitch/python/ovs/stream.py
/usr/share/openvswitch/python/ovs/timeval.py
/usr/share/openvswitch/python/ovs/util.py
/usr/share/openvswitch/python/uuid.py
/usr/share/openvswitch/scripts/ovs-xapi-sync
/usr/share/openvswitch/scripts/interface-reconfigure
/usr/share/openvswitch/scripts/InterfaceReconfigure.py
/usr/share/openvswitch/scripts/InterfaceReconfigureBridge.py
/usr/share/openvswitch/scripts/InterfaceReconfigureVswitch.py
/usr/share/openvswitch/scripts/vif
/usr/share/openvswitch/scripts/sysconfig.template
/usr/share/openvswitch/scripts/xen-bugtool-tc-class-show
/usr/share/openvswitch/scripts/ovs-save
/usr/share/openvswitch/vswitch.ovsschema
/usr/sbin/ovs-vswitchd
/usr/sbin/ovsdb-server
/usr/bin/ovs-appctl
/usr/bin/ovs-dpctl
/usr/bin/ovs-ofctl
/usr/bin/ovs-pcap
/usr/bin/ovs-tcpundump
/usr/bin/ovs-vlan-test
/usr/bin/ovs-vsctl
/usr/bin/ovsdb-client
/usr/bin/ovsdb-tool
/usr/lib/xsconsole/plugins-base/XSFeatureVSwitch.py
/usr/share/man/man1/ovsdb-client.1.gz
/usr/share/man/man1/ovsdb-server.1.gz
/usr/share/man/man1/ovsdb-tool.1.gz
/usr/share/man/man5/ovs-vswitchd.conf.db.5.gz
/usr/share/man/man8/ovs-appctl.8.gz
/usr/share/man/man8/ovs-dpctl.8.gz
/usr/share/man/man8/ovs-ofctl.8.gz
/usr/share/man/man8/ovs-parse-leaks.8.gz
/usr/share/man/man1/ovs-pcap.1.gz
/usr/share/man/man1/ovs-tcpundump.1.gz
/usr/share/man/man8/ovs-vlan-test.8.gz
/usr/share/man/man8/ovs-vsctl.8.gz
/usr/share/man/man8/ovs-vswitchd.8.gz
/var/lib/openvswitch
%exclude /usr/lib/xsconsole/plugins-base/*.py[co]
%exclude /usr/sbin/ovs-brcompatd
%exclude /usr/share/man/man8/ovs-brcompatd.8.gz
%exclude /usr/share/openvswitch/scripts/*.py[co]
%exclude /usr/share/openvswitch/python/*.py[co]
%exclude /usr/share/openvswitch/python/ovs/*.py[co]
%exclude /usr/share/openvswitch/python/ovs/db/*.py[co]

%files %{module_package}
/lib/modules/%{xen_version}/kernel/extra/openvswitch/openvswitch_mod.ko
%exclude /lib/modules/%{xen_version}/kernel/extra/openvswitch/brcompat_mod.ko
