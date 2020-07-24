# vServer
A modular python script wich starts a video deembedder and rtp videostreamer.
It can be remote controlled by mqtt commands.

For testing and codec selection the script can be used with a interactive user dialog and CPU-, Memory- and Networkusage are logged.

### Dependencies:
* gstreamer (https://gstreamer.freedesktop.org/)
* a bunch of video- and audiocodecs
* paho mqtt client for remote
* nmon for logging