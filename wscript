#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# WAF build script
#
# Copyright 2008-2009 Enrico Tröger <enrico(at)xfce(dot)org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# $Id$



import Build, Configure, Options, Utils, UnitTest
import sys, os, shutil


APPNAME = 'gigolo'
VERSION = '0.3.2'

srcdir = '.'
blddir = '_build_'


sources = [ 'src/compat.c', 'src/window.c', 'src/bookmark.c', 'src/settings.c',
			'src/menubuttonaction.c', 'src/mountoperation.c', 'src/bookmarkdialog.c',
			'src/bookmarkeditdialog.c', 'src/preferencesdialog.c', 'src/backendgvfs.c',
			'src/common.c', 'src/mountdialog.c', 'src/browsenetworkpanel.c',
			'src/singleinstance.c' ]



def configure(conf):
	conf.check_tool('compiler_cc intltool misc gnu_dirs')

	conf.check_cfg(package='gtk+-2.0', atleast_version='2.12.0', uselib_store='GTK',
		mandatory=True, args='--cflags --libs')
	conf.check_cfg(package='gio-2.0', atleast_version='2.16.0', uselib_store='GIO',
		mandatory=True, args='--cflags --libs')

	gtk_version = conf.check_cfg(modversion='gtk+-2.0', uselib_store='GTK')
	gio_version = conf.check_cfg(modversion='gio-2.0', uselib_store='GIO')

	conf.define('GETTEXT_PACKAGE', APPNAME, 1)
	conf.define('PACKAGE', APPNAME, 1)
	conf.define('VERSION', VERSION, 1)

	conf.write_config_header('config.h')

	# debug flags
	if Options.options.debug:
		conf.env.append_value('CCFLAGS', '-g -O0 -DDEBUG '.split())

	Utils.pprint('BLUE', 'Summary:')
	print_message(conf, 'Install Gigolo ' + VERSION + ' in', conf.env['PREFIX'])
	print_message(conf, 'Using GTK version', gtk_version or 'Unknown')
	print_message(conf, 'Using GIO version', gio_version or 'Unknown')
	print_message(conf, 'Compiling with debugging support', Options.options.debug and 'yes' or 'no')


def set_options(opt):
	opt.tool_options('compiler_cc')
	opt.tool_options('intltool')
	opt.tool_options('gnu_dirs')

	# Features
	opt.add_option('--enable-debug', action='store_true', default=False,
		help='enable debug mode [default: No]', dest='debug')
	opt.add_option('--update-po', action='store_true', default=False,
		help='update the message catalogs for translation', dest='update_po')


def build(bld):
	def add_tests(bld):
		tests = os.listdir('tests')
		for test in tests:
			if test[-2:] != '.c':
				continue
			target = test[:-2]
			source = os.path.join("tests", test)

		bld.new_task_gen(
			features		= 'cc cprogram',
			target			= 'test-' + target,
			source			= source,
			includes		= '. src',
			uselib			= 'GTK GIO',
			uselib_local	= 'gigolo_lib',
			unit_test		= 1,
			install_path	= None
		)


	bld.new_task_gen(
		features		= 'cc cstaticlib',
		name			= 'gigolo_lib',
		target			= 'gigolo_lib',
		source			= sources,
		includes		= '.',
		uselib			= 'GTK GIO',
		install_path	= None
	)

	bld.new_task_gen(
		features		= 'cc cprogram',
		name			= 'gigolo',
		target			= 'gigolo',
		source			= 'src/main.c',
		includes		= '.',
		uselib			= 'GTK GIO',
		uselib_local	= 'gigolo_lib',
	)

	if Options.commands['check']:
		add_tests(bld)

	# Translations
	bld.new_task_gen(
		features		= 'intltool_po',
		podir			= 'po',
		appname			= 'gigolo'
	)

	# gigolo.desktop
	bld.new_task_gen(
		features		= 'intltool_in',
		source			= 'gigolo.desktop.in',
		flags			= '-d',
		install_path	= '${DATADIR}/applications'
	)

	# gigolo.1
	bld.new_task_gen(
		features		= 'subst',
		source			= 'gigolo.1.in',
		target			= 'gigolo.1',
		dict			= { 'VERSION' : VERSION },
		install_path	= '${MANDIR}/man1'
	)

	# Docs
	bld.install_files('${DOCDIR}', 'AUTHORS ChangeLog COPYING README NEWS TODO')


def dist():
	import md5
	from Scripting import dist, excludes
	excludes.append('gigolo-%s.tar.bz2.sig' % VERSION)
	filename = dist(APPNAME, VERSION)
	f = file(filename,'rb')
	m = md5.md5()
	readBytes = 100000
	while (readBytes):
		readString = f.read(readBytes)
		m.update(readString)
		readBytes = len(readString)
	f.close()
	launch('gpg --detach-sign --digest-algo SHA512 %s' % filename, 'Signing %s' % filename)
	print 'MD5 sum:', filename, m.hexdigest()
	sys.exit(0)


def shutdown():
	# the following code was taken from midori's WAF script, thanks
	# (disabled because we don't need it at all as long as we don't have an own icon :( )
	#~ if Options.commands['install'] or Options.commands['uninstall']:
		#~ dir = Build.bld.get_install_path('${DATADIR}/icons/hicolor')
		#~ icon_cache_updated = False
		#~ if not Options.options.destdir:
			#~ try:
				#~ if not Utils.exec_command('gtk-update-icon-cache -q -f -t %s' % dir):
					#~ Utils.pprint('YELLOW', "Updated Gtk icon cache.")
					#~ icon_cache_updated = True
			#~ except:
				#~ Utils.pprint('RED', "Failed to update icon cache.")
		#~ if not icon_cache_updated:
			#~ Utils.pprint('YELLOW', "Icon cache not updated. After install, run this:")
			#~ Utils.pprint('YELLOW', "gtk-update-icon-cache -q -f -t %s" % dir)
	if Options.options.update_po:
		os.chdir(os.path.join(srcdir, 'po'))
		try:
			try:
				size_old = os.stat('gigolo.pot').st_size
			except:
				size_old = 0
			Utils.exec_command(['intltool-update', '--pot', '-g', APPNAME])
			size_new = os.stat('gigolo.pot').st_size
			if size_new != size_old:
				Utils.pprint('CYAN', 'Updated POT file.')
				launch('intltool-update -r %s' % APPNAME, 'Updating translations', 'CYAN')
			else:
				Utils.pprint('CYAN', 'POT file is up to date.')
		except:
			Utils.pprint('RED', 'Failed to generate pot file.')
		os.chdir('..')


def check(ch):
	test = UnitTest.unit_test()
	test.change_to_testfile_dir = False
	test.want_to_see_test_output = True
	test.want_to_see_test_error = True
	test.run()
	test.print_results()


# Simple function to execute a command and print its exit status
def launch(command, status, success_color='GREEN'):
	ret = 0
	Utils.pprint(success_color, status)
	try:
		ret = Utils.exec_command(command.split())
	except:
		ret = 1

	if ret != 0:
		Utils.pprint('RED', status + ' failed')

	return ret

def print_message(conf, msg, result, color = 'GREEN'):
	conf.check_message_1(msg)
	conf.check_message_2(result, color)
