Name:           bcc
Version:        0.13.0
Release:        2
Summary:        BPF Compiler Collection (BCC)
License:        ASL 2.0
URL:            https://github.com/iovisor/bcc
# Upstream now provides a release with the git submodule embedded in it
Source0:        %{url}/archive/%{name}-%{version}.tar.gz

# Arches will be included as upstream support is added and dependencies are
# satisfied in the respective arches

BuildRequires:  bison cmake >= 2.8.7 flex libxml2-devel python3-devel
BuildRequires:  elfutils-libelf-devel llvm-devel clang-devel
BuildRequires:  llvm-static ncurses-devel pkgconfig(luajit)
BuildRequires:  libbpf-devel >= 0.0.5-3, libbpf-static >= 0.0.5-3
# Additional dependency on util-linux for 'rename'
BuildRequires:  util-linux

Requires:       %{name}-tools = %{version}-%{release}
Requires:       libbpf >= 0.0.5-3

%description
BCC is a toolkit for creating efficient kernel tracing and manipulation
programs, and includes several useful tools and examples. It makes use of
extended BPF (Berkeley Packet Filters), formally known as eBPF, a new feature
that was first added to Linux 3.15. BCC makes BPF programs easier to write,
with kernel instrumentation in C (and includes a C wrapper around LLVM), and
front-ends in Python and lua. It is suited for many tasks, including
performance analysis and network traffic control.


%package devel
Summary:        Shared library for BPF Compiler Collection (BCC)
Requires:       %{name} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for developing
application that use BPF Compiler Collection (BCC).


%package help 
Summary:        Examples for BPF Compiler Collection (BCC)
Requires:       man info
Recommends:     python3-%{name} = %{version}-%{release}
Recommends:     %{name}-lua = %{version}-%{release}
BuildArch:      noarch

%description help
Examples for BPF Compiler Collection (BCC)


%package -n python3-bpfcc
Summary:        Python3 bindings for BPF Compiler Collection (BCC)
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch
%{?python_provide:%python_provide python3-bpfcc}

%description -n python3-bpfcc
Python3 bindings for BPF Compiler Collection (BCC)


%package lua
Summary:        Standalone tool to run BCC tracers written in Lua
Requires:       %{name} = %{version}-%{release}

%description lua
Standalone tool to run BCC tracers written in Lua

%package tools
Summary:        Command line tools for BPF Compiler Collection (BCC)
Requires:       python3-bpfcc = %{version}-%{release}
Requires:       python3-netaddr
Requires:       kernel-devel

%description tools
Command line tools for BPF Compiler Collection (BCC)


%prep
%autosetup -n %{name} -p1

%build
%cmake . \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DREVISION_LAST=%{version} -DREVISION=%{version} -DPYTHON_CMD=python3 \
        -DCMAKE_USE_LIBBPF_PACKAGE:BOOL=TRUE \
        %{?with_llvm_shared:-DENABLE_LLVM_SHARED=1}

%make_build


%install
%make_install

# Fix python shebangs
find %{buildroot}%{_datadir}/%{name}/{tools,examples} -type f -exec \
  sed -i -e '1s=^#!/usr/bin/python\([0-9.]\+\)\?$=#!%{__python3}=' \
         -e '1s=^#!/usr/bin/env python\([0-9.]\+\)\?$=#!%{__python3}=' \
         -e '1s=^#!/usr/bin/env bcc-lua$=#!/usr/bin/bcc-lua=' {} \;

# Move man pages to the right location
mkdir -p %{buildroot}%{_mandir}
mv %{buildroot}%{_datadir}/%{name}/man/* %{buildroot}%{_mandir}/

mv %{buildroot}%{python3_sitelib}/%{name} %{buildroot}%{python3_sitelib}/bpfcc
rename %{name} bpfcc %{buildroot}%{python3_sitelib}/%{name}-*egg-info

# Avoid conflict with other manpages
# https://bugzilla.redhat.com/show_bug.cgi?id=1517408
for i in `find %{buildroot}%{_mandir} -name "*.gz"`; do
  tname=$(basename $i)
  rename $tname %{name}-$tname $i
done
mkdir -p %{buildroot}%{_docdir}/%{name}
mv %{buildroot}%{_datadir}/%{name}/examples %{buildroot}%{_docdir}/%{name}/

# Delete old tools we don't want to ship
rm -rf %{buildroot}%{_datadir}/%{name}/tools/old/

# We cannot run the test suit since it requires root and it makes changes to
# the machine (e.g, IP address)
#%check

%ldconfig_scriptlets

%files
%doc README.md
%license LICENSE.txt
%{_libdir}/lib%{name}.so.*
%{_libdir}/libbcc_bpf.so.*
%{_libdir}/libbcc-no-libbpf.so.*

%files devel
%exclude %{_libdir}/lib%{name}*.a
%exclude %{_libdir}/lib%{name}*.la
%{_libdir}/lib%{name}.so
%{_libdir}/libbcc_bpf.so
%{_libdir}/libbcc-no-libbpf.so
%{_libdir}/pkgconfig/lib%{name}.pc
%{_includedir}/%{name}/

%files -n python3-bpfcc
%{python3_sitelib}/bpfcc*

%files help
%dir %{_docdir}/%{name}
%doc %{_docdir}/%{name}/examples/
%{_mandir}/man8/*

%files tools
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/tools/
%{_datadir}/%{name}/introspection/

%files lua
%{_bindir}/bcc-lua


%changelog
* Fri Jul 17 2020 Shinwell Hu <micromotive@qq.com> - 0.13.0-2
- Rename python3-bcc to python3-bpfcc to avoid confliction with bcc on pypi

* Sun Apr 26 2020 openEuler Buildteam <buildteam@openeuler.org> - 0.13.0-1
- Package init
