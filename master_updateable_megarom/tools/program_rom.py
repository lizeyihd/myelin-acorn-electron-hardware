# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Program a 128kB, 256kB, or 512kB ROM image into a master_updateable_megarom
# board.

import re
import megarom
import sys
import time

def read_until(ser, match):
    resp = ''
    while 1:
        r = ser.read(1024)
        if r:
            print `r`
            resp += r
            if resp.find(match) != -1:
                break
            else:
                time.sleep(0.1)
    return resp

def main():
    rom_fn, = sys.argv[1:]
    rom = open(rom_fn).read()

    with megarom.Port() as ser:
        print "\n* Port open.  Giving it a kick, and waiting for OK."
        ser.write("\n")
        r = read_until(ser, "OK")

        print "\n* Requesting chip ID and locking chip"
        ser.write("I\n")  # identify chip
        r = read_until(ser, "OK")
        m = re.search("Size = (\d+)", r)
        if not m:
            raise Exception("Chip identification failed")
        chip_size = int(m.group(1))
        print "\n* Chip size = %d bytes" % chip_size

        if len(rom) != chip_size:
            raise Exception("%s is %d bytes long, which does not match the flash capacity of %d bytes" % (rom_fn, len(rom), chip_size))

        print "\n* Start programming process"
        ser.write("P\n")  # program chip

        input_buf = ''
        done = 0
        while not done:
            input_buf += read_until(ser, "\n")
            while input_buf.find("\n") != -1:
                p = input_buf.find("\n") + 1
                line, input_buf = input_buf[:p], input_buf[p:]
                line = line.strip()
                print "parse",`line`
                if line == "OK":
                    print "All done!"
                    done = 1
                    break
                m = re.search("^(\d+)\+(\d+)$", line)
                if not m: continue

                start, size = int(m.group(1)), int(m.group(2))
                print "* Sending data from %d-%d" % (start, start+size)
                blk = rom[start:start+size]
                while len(blk):
                    n = ser.write(blk[:63])
                    if n:
                        blk = blk[n:]
                        print "wrote %d bytes" % n
                    else:
                        time.sleep(0.01)


if __name__ == '__main__':
    main()
