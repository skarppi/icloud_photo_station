#!/bin/bash

PKG_DIR=_spk
TGZ_DIR=_tgz

PKG_UTIL='pkg_util.sh'

VIRTUALENV='virtualenv-15.1.0.tar.gz'

clean() {
	rm -fr $PKG_DIR
	rm -fr $TGZ_DIR

	#rm _${PKG_UTIL}
	#rm _${VIRTUALENV}
}

setup() {

	# download a helper script for creating Synology packages
	if [ ! -f _${PKG_UTIL} ]; then
	    wget -O _${PKG_UTIL} https://raw.githubusercontent.com/SynologyOpenSource/pkgscripts-ng/master/include/${PKG_UTIL}
	fi
	source $PWD/_${PKG_UTIL}

	# download virtualenv distribution to be included in our installation package
	if [ ! -f _${VIRTUALENV} ]; then
		wget -O _${VIRTUALENV} https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/${VIRTUALENV}
	fi

	mkdir -p $PKG_DIR
	mkdir -p $TGZ_DIR
}

create_package_tgz() {
	# Install virtual env and all libraries
	tar xvfz _${VIRTUALENV} -C $TGZ_DIR
	pip wheel --wheel-dir=${TGZ_DIR}/wheelhouse -r ../requirements.txt

	# Copy python app
	mkdir -p ${TGZ_DIR}/app
	cp -av ../*.py $TGZ_DIR/app

	mkdir -p ${TGZ_DIR}/app/icloudpd
	cp -av ../icloudpd/*.py $TGZ_DIR/app/icloudpd

	# ### create package.tgz $1: source_dir $2: dest_dir
	pkg_make_package $TGZ_DIR "${PKG_DIR}"
}

create_spk() {
	local scripts_dir=$PKG_DIR/scripts

	### Copy package center scripts to PKG_DIR
	mkdir -p $scripts_dir
	cp -av scripts/* $scripts_dir

	### Copy package icon
	cp -av PACKAGE_ICON*.PNG $PKG_DIR

	### Copy INFO file
	cp -av INFO $PKG_DIR/INFO

	### Create the final spk.
	# pkg_make_spk <source path> <dest path> <spk file name>
	# Please put the result spk into /image/packages
	# spk name functions: pkg_get_spk_name pkg_get_spk_unified_name pkg_get_spk_family_name
	pkg_make_spk ${PKG_DIR} . $(pkg_get_spk_family_name)
}

clean
setup
create_package_tgz
create_spk

clean