import glob

__version__ = '0.0.1'

setup_args = {
	'name': 'pyganglia_dbi',
	'author': 'Immanuel Washington',
	'author_email': 'immwa at sas.upenn.edu',
	'license': 'GPL',
	'package_dir' : {'pyganglia_dbi': ''},
	'packages' : ['pyganglia_dbi'],
	'scripts': glob.glob('scripts/*'),
	'version': __version__,
}

if __name__ == '__main__':
	from distutils.core import setup
	apply(setup, (), setup_args)
