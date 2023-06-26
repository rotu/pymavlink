from setuptools.command.build_py import build_py
from io import open
# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs')
    codecs.register(func)

from setuptools import setup
import glob, os, shutil, fnmatch, sys

sys.path.insert(0, os.path.dirname(__file__))
from __init__ import __version__

def generate_content():
    # generate the file content...
    from generator import mavgen, mavparse

    # path to message_definitions directory
    if os.getenv("MDEF",None) is not None:
        mdef_paths = [os.getenv("MDEF")]

    else:
        mdef_paths = [os.path.join('..', 'message_definitions'),
                      os.path.join('mavlink', 'message_definitions'),
                      os.path.join('..', 'mavlink', 'message_definitions'),
                      os.path.join('message_definitions'),
        ]

    for path in mdef_paths:
        mdef_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
        if os.path.exists(mdef_path):
            print("Using message definitions from %s" % mdef_path)
            break

    dialects_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dialects')

    v10_dialects = glob.glob(os.path.join(mdef_path, 'v1.0', '*.xml'))

    # for now v2.0 uses same XML files as v1.0
    v20_dialects = glob.glob(os.path.join(mdef_path, 'v1.0', '*.xml'))

    should_generate = not "NOGEN" in os.environ
    if should_generate:
        if len(v10_dialects) == 0:
            print("No XML message definitions found")
            sys.exit(1)

        for xml in v10_dialects:
            shutil.copy(xml, os.path.join(dialects_path, 'v10'))
        for xml in v20_dialects:
            shutil.copy(xml, os.path.join(dialects_path, 'v20'))

        for xml in v10_dialects:
            dialect = os.path.basename(xml)[:-4]
            wildcard = os.getenv("MAVLINK_DIALECT",'*')
            if not fnmatch.fnmatch(dialect, wildcard):
                continue
            print("Building %s for protocol 1.0" % xml)
            if not mavgen.mavgen_python_dialect(dialect, mavparse.PROTOCOL_1_0, with_type_annotations=True):
                print("Building failed %s for protocol 1.0" % xml)
                sys.exit(1)
            if not mavgen.mavgen_python_dialect(dialect, mavparse.PROTOCOL_1_0, with_type_annotations=False):
                print("Building failed %s (without type annotations) for protocol 1.0" % xml)
                sys.exit(1)

        for xml in v20_dialects:
            dialect = os.path.basename(xml)[:-4]
            wildcard = os.getenv("MAVLINK_DIALECT",'*')
            if not fnmatch.fnmatch(dialect, wildcard):
                continue
            print("Building %s for protocol 2.0" % xml)
            if not mavgen.mavgen_python_dialect(dialect, mavparse.PROTOCOL_2_0, with_type_annotations=True):
                print("Building failed %s for protocol 2.0" % xml)
                sys.exit(1)
            if not mavgen.mavgen_python_dialect(dialect, mavparse.PROTOCOL_2_0, with_type_annotations=False):
                print("Building failed %s (Python3.5) for protocol 2.0" % xml)
                sys.exit(1)


class custom_build_py(build_py):
    def run(self):
        generate_content()

        # distutils uses old-style classes, so no super()
        build_py.run(self)

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup (name = 'pymavlink',
       version = __version__,
       description = 'Python MAVLink code',
       long_description = long_description,
       long_description_content_type = "text/markdown",
       url = 'https://github.com/ArduPilot/pymavlink/',
       classifiers=['Development Status :: 5 - Production/Stable',
                    'Environment :: Console',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 3.6',
                    'Programming Language :: Python :: 3.7',
                    'Programming Language :: Python :: 3.8',
                    'Programming Language :: Python :: 3.9',
                    'Topic :: Scientific/Engineering',
                    ],
       license='LGPLv3',
       package_dir = { 'pymavlink' : '.' },
       package_data = { 'pymavlink.dialects.v10' : ['*.xml'],
                        'pymavlink.dialects.v20' : ['*.xml'],
                        'pymavlink.generator'    : [ '*.xsd',
                                                     'java/lib/*.*',
                                                     'java/lib/Messages/*.*',
                                                     'C/include_v1.0/*.h',
                                                     'C/include_v1.0/*.hpp',
                                                     'C/include_v2.0/*.h',
                                                     'C/include_v2.0/*.hpp',
                                                     'CPP11/include_v2.0/*.hpp',
                                                     'CS/*.*',
                                                     'swift/*.swift',],
                        'pymavlink'              : ['message_definitions/v*/*.xml']
                        },
       packages = ['pymavlink',
                   'pymavlink.generator',
                   'pymavlink.dialects',
                   'pymavlink.dialects.v10',
                   'pymavlink.dialects.v10.python2',
                   'pymavlink.dialects.v20',
                   'pymavlink.dialects.v20.python2'],
       scripts = [ 'tools/magfit_delta.py', 'tools/mavextract.py',
                   'tools/mavgraph.py', 'tools/mavparmdiff.py',
                   'tools/mavtogpx.py', 'tools/magfit_gps.py',
                   'tools/mavflightmodes.py', 'tools/mavlogdump.py',
                   'tools/mavparms.py', 'tools/magfit_motors.py',
                   'tools/mavflighttime.py', 'tools/mavloss.py',
                   'tools/mavplayback.py', 'tools/magfit.py',
                   'tools/mavgpslock.py',
                   'tools/mavmission.py',
                   'tools/mavsigloss.py',
                   'tools/mavsearch.py',
                   'tools/mavtomfile.py',
                   'tools/mavgen.py',
                   'tools/mavkml.py',
                   'tools/mavfft.py',
                   'tools/mavfft_isb.py',
                   'tools/mavsummarize.py',
                   'tools/MPU6KSearch.py',
                   'tools/mavlink_bitmask_decoder.py',
                   'tools/magfit_WMM.py',
       ],
       install_requires=[
            'lxml',
       ],
       cmdclass={'build_py': custom_build_py},
       )
