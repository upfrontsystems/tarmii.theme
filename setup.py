from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='tarmii.theme',
      version=version,
      description="Theme for TARMII",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tarmii'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.registry',          
          'plone.app.theming',
          'collective.quickupload',
          'requests',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      extras_require = {
          'test': [
                  'plone.app.testing',
              ]
      },
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
