##########################
# Heavily base on a package by Sean Reifschneider <jafo-rpms@tummy.com>
# and Keith Dart <keith.dart@thalesesec.com>
##########################

##########################
#  User-modifiable configs
##########################

#  Is the resulting package and the installed binary named "python" or
#  "python2"?
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_binsuffix 2.7

#  Use pymalloc?  The last line (commented or not) determines wether
#  pymalloc is used.
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_pymalloc yes

#  Enable IPV6?
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_ipv6 yes

#  Location of the HTML directory.
%define config_htmldir /var/www/html/python

#################################
#  End of user-modifiable configs
#################################

%define name python27
#--start constants--
%define version 2.7.6rc1
%define libvers 2.7
%define virtualenvversion 1.9.1
#--end constants--
%define release 1
%define __prefix /usr/local

#  kludge to get around rpm <percent>define weirdness
%define ipv6 %(if [ "%{config_ipv6}" = yes ]; then echo --enable-ipv6; else echo --disable-ipv6; fi)
%define pymalloc %(if [ "%{config_pymalloc}" = yes ]; then echo --with-pymalloc; else echo --without-pymalloc; fi)
%define binsuffix %(if [ "%{config_binsuffix}" = none ]; then echo ; else echo "%{config_binsuffix}"; fi)
#%define libdirname %(( uname -m | egrep -q '_64$' && [ -d /usr/lib64 ] && echo lib64 ) || echo lib)
%define libdirname lib

Summary: An interpreted, interactive, object-oriented programming language.
Name: python27
Version: %{version}
Release: %{release}
License: PSF
Group: Development/Languages
Source: Python-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: gcc make expat-devel db4-devel gdbm-devel sqlite-devel readline-devel zlib-devel bzip2-devel openssl-devel
AutoReq: no
Prefix: %{__prefix}
Packager: Joep Driesen <joep.driesen@seasoning.com>

%description
Python is an interpreted, interactive, object-oriented programming
language.  It incorporates modules, exceptions, dynamic typing, very high
level dynamic data types, and classes. Python combines remarkable power
with very clear syntax. It has interfaces to many system calls and
libraries, as well as to various window systems, and is extensible in C or
C++. It is also usable as an extension language for applications that need
a programmable interface.  Finally, Python is portable: it runs on many
brands of UNIX, on PCs under Windows, MS-DOS, and OS/2, and on the
Mac.

%changelog
* Wed Dec 4 2013 Joep Driesen <joep.driesen@seasoning.com>
- First version

#######
#  PREP
#######
%prep
%setup -n Python-%{version}
rm -rf /tmp/virtualenv-%{virtualenvversion}
tar -xzf $RPM_SOURCE_DIR/virtualenv-%{virtualenvversion}.tar.gz -C /tmp

########
#  BUILD
########
%build
echo "Setting for ipv6: %{ipv6}"
echo "Setting for pymalloc: %{pymalloc}"
echo "Setting for binsuffix: %{binsuffix}"
./configure --enable-unicode=ucs4 --with-signal-module --with-threads %{ipv6} %{pymalloc} --prefix=%{__prefix}
make %{_smp_mflags}

##########
#  INSTALL
##########
%install
#  set the install path
echo '[install_scripts]' >setup.cfg
echo 'install_dir='"${RPM_BUILD_ROOT}%{__prefix}/bin" >>setup.cfg

[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/lib-dynload
make prefix=$RPM_BUILD_ROOT%{__prefix} altinstall

#  REPLACE PATH IN PYDOC
if [ ! -z "%{binsuffix}" ]
then
   (
      cd $RPM_BUILD_ROOT%{__prefix}/bin
      mv pydoc pydoc.old
      sed 's|#!.*|#!%{__prefix}/bin/python'%{binsuffix}'|' \
            pydoc.old >pydoc
      chmod 755 pydoc
      rm -f pydoc.old
      sed -i -e 's|#!.*|#!%{__prefix}/bin/python'%{binsuffix}'|' python%{libvers}-config
   )
fi

#  add the binsuffix
if [ ! -z "%{binsuffix}" ]
then
   ( cd $RPM_BUILD_ROOT%{__prefix}/bin; 
      for file in 2to3  pydoc  python-config  idle smtpd.py; do [ -f "$file" ] && mv "$file" "$file"%{binsuffix}; done;)
fi

# Fix permissions
chmod 644 $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/libpython%{libvers}*

#  check to see if there are any straggling #! lines
#find "$RPM_BUILD_ROOT" -type f | xargs egrep -n '^#! */usr/local/bin/python' \
#      | grep ':1:#!' >/tmp/python-rpm-files.$$ || true
#if [ -s /tmp/python-rpm-files.$$ ]
#then
#   echo '*****************************************************'
#   cat /tmp/python-rpm-files.$$
#   cat <<@EOF
#   *****************************************************
#     There are still files referencing /usr/local/bin/python in the
#     install directory.  They are listed above.  Please fix the .spec
#     file and try again.  If you are an end-user, you probably want
#     to report this to jafo-rpms@tummy.com as well.
#   *****************************************************
#@EOF
#   rm -f /tmp/python-rpm-files.$$
#   exit 1
#fi
#rm -f /tmp/python-rpm-files.$$

# Install virtualenv
prevdir=`pwd`
cd /tmp/virtualenv-%{virtualenvversion}/
$RPM_BUILD_ROOT%{__prefix}/bin/python%{binsuffix} setup.py install
cd $prevdir


########
#  CLEAN
########
%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

########
#  FILES
########
%files
/usr/local/bin/virtualenv-2.7
/usr/local/bin/python2.7-config
/usr/local/bin/virtualenv
/usr/local/bin/python2.7
/usr/local/include/python2.7/pyconfig.h
%defattr(-,root,root)
%doc Misc/README Misc/cheatsheet Misc/Porting
%doc LICENSE Misc/ACKS Misc/HISTORY Misc/NEWS
%doc %{__prefix}/share/man/man1/python2.7.1

%attr(755,root,root) %dir %{__prefix}/include/python%{libvers}
%attr(755,root,root) %dir %{__prefix}/lib/python%{libvers}/
%attr(755,root,root) %dir %{__prefix}/%{libdirname}/python%{libvers}/