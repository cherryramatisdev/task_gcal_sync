from setuptools import setup

description = "task warrior google calendar sync script"
long_description = description

setup(
    name="task_gcal_sync",
    version="0.1",
    author="mehdi cherti",
    author_email="mehdicherti@gmail.com",
    description=description,
    long_description=long_description,
    license="MIT",
    keywords="task-warrior google-calendar calendar",
    url="https://github.com/mehdidc/task_gcal_sync",
    zip_safe=False,  # the package can run out of an .egg file
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved',
                 'Programming Language :: Python',
                 'Topic :: Software Development',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'Operating System :: Unix',
                 'Operating System :: MacOS'],
    platforms='any',
    scripts=['task_gcal_sync'],
    install_requires=['google-api-python-client', 'taskw'],
)
