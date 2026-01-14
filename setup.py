from setuptools import find_packages, setup

__version__ = '0.0.4'
URL = 'https://github.com/tbohne/nesy_diag_ontology'

with open('requirements.txt') as f:
    required = f.read().splitlines()

for i in range(len(required)):
    # adapt the repo references for setup.py usage
    if "https" in required[i]:
        pkg = required[i].split(".git")[0].split("/")[-1]
        required[i] = pkg + "@" + required[i]

setup(
    name='nesy_diag_ontology',
    version=__version__,
    description='Ontology (KG) for capturing knowledge about neuro-symbolic diagnostics '
                '- knowledge acquisition, enhancement & retrieval.',
    author='Tim Bohne',
    author_email='tim.bohne@dfki.de',
    url=URL,
    download_url=f'{URL}/archive/{__version__}.tar.gz',
    keywords=[
        'sparql',
        'rdf',
        'semantic-web',
        'ontology',
        'knowledge-graph',
        'knowledge-base'
    ],
    python_requires='>=3.7',
    install_requires=required,
    packages=find_packages(),
    include_package_data=True,
)
