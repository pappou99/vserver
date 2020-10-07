# vServer

A modular python script wich starts a video deembedder and rtp videostreamer.
It can be remote controlled by mqtt commands.

For testing and codec selection the script can be used with a interactive user dialog and CPU-, Memory- and Networkusage are logged.

**WARNING: This script is still early apha status and may be buggy!**

### Dependencies:

* gstreamer (https://gstreamer.freedesktop.org/)
* gi python-gstreamer bindings
* a bunch of video- and audiocodecs
* paho mqtt client for remote
* nmon for logging
