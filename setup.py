from setuptools import setup, find_packages
import gmaps_places

setup(
    name='twentytab-gmaps-places',
    version=gmaps_places.__version__,
    description='A django app on top of twentytab-gmaps and google maps api v3 to manage geolocation and markers with all the administrative level details',
    author='20tab S.r.l.',
    author_email='info@20tab.com',
    url='https://github.com/20tab/twentytab-gmaps-places',
    license='MIT License',
    install_requires=[
        'Django >=1.6',
        'django-appconf>=0.6',
        'twentytab-gmaps>=0.12',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
    }
)
