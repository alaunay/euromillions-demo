%global _python_dist_allow_version_zero 1

Name:           terminal-svg-demo
Version:        0.0.0
Release:        1%{?dist}
Summary:        Render an animated terminal session as declarative SVG

License:        GPL-3.0-or-later
URL:            https://github.com/alaunay/terminal-svg-demo
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  gettext
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
Render a command line session as a self-playing SVG animation, from a
JSON spec. The animation uses SMIL, so it needs no JavaScript, no media
player, and no dependency beyond the Python standard library.

%prep
%autosetup -n %{name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files terminal_svg_demo
tools/build-locales.sh
install -d %{buildroot}%{_datadir}/terminal-svg-demo
cp -a src/terminal_svg_demo/locale %{buildroot}%{_datadir}/terminal-svg-demo/

%check
%pyproject_check_import

%files -f %{pyproject_files}
%{_bindir}/terminal-svg-demo
%{_datadir}/terminal-svg-demo

%changelog
* Mon Nov 09 2026 Arnaud Launay <asl@launay.org> - 0.0.0-1
- Unreleased.
