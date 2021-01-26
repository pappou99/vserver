"""

Run the jack_control program, with source code linked below, from Python.
   https://github.com/jackaudio/jack2/blob/develop/tools/jack_control

"""

import sys
# sys.path.append('../bin_helper/jack_control')
import io
import vserver.jack_control as jc  # Must be in `sys.path` list with `.py` extension.


class FakeSys:
    pass


jc.sys = FakeSys  # Override the `sys` module that was imported in jc.


class JackControl:
    def __init__(self):
        pass

    def jack_control(*args):
        """Run `jack_control` as if it were called from the command-line with the
        parameter strings as command-line arguments.  Returns the exit code and
        the string that would have been written to stdout."""
        args = [str(a) for a in args]  # Convert any ints which were passed in.
        jc.sys.argv = ["jack_control"] + args

        old_sys_stdout = sys.stdout
        sys.stdout = io.StringIO()
        retcode = jc.main()  # Call the real `jack_control` function.
        msg = sys.stdout.getvalue()
        sys.stdout = old_sys_stdout

        return retcode, msg


# Test.
if __name__ == "__main__":

    exit_code, msg = jack_control("help")  # Get help message.
    print(msg)  # Print the help message (redirected from stdout).

    # Toggle start/stop state.
    status_code, msg = jack_control("status")
    if status_code == 0:
        jack_control("stop")
    else:
        jack_control("start")
    print("Status msg is:\n", msg)

    # Get the long description for the engine parameter "driver".
    exit_code, msg = jack_control("epd", "driver")
    print(msg)

    # Set the "rate" parameter.
    exit_code, msg = jack_control("dps", "rate", 44100)
    print("Rate set exit code was:", exit_code)
    print("Rate set msg:\n", msg, sep="")
