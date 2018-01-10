Extract installed packages from a Docker image - pkgextract
===========================================================

Tool pkgextract is a simple utility that uses `mercator-go <https://github.com/fabric8-analytics/mercator-go>`_ and `container-diff <https://github.com/GoogleCloudPlatform/container-diff>`_ for extracting information about installed PyPI and RPM packages inside a Docker image.


Installation
------------

Simply clone this repo and run ``docker build``.

.. code-block:: console

  $ git clone https://github.com/fridex/pkgextractor.git
  $ cd pkgextractor
  $ docker build . -t pkgextract
  ...


Running pkgextract
------------------

See shipped help for info about provided commands:

.. code-block:: console

  $ docker run -v /var/run/docker.sock:/var/run/docker.sock pkgextract --help
  $ # To analyze an image:
  $ docker run --privileged -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker pkgextract -vvvv analyze -i fedora:27
  ...

