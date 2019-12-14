# bdevice.py Hardware-agnostic base class for block devices.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019 Peter Hinch

# Hardware-independent class implementing the uos.AbstractBlockDev protocol with
# simple and extended interface. It should therefore support littlefs.
# http://docs.micropython.org/en/latest/reference/filesystem.html#custom-block-devices

# The subclass must implement .readwrite which can read or write arbitrary amounts
# of data to arbitrary addresses. IOW .readwrite handles physical block structure
# while ioctl supports a virtual block size.

class BlockDevice:

    def __init__(self, nbits, nchips, chip_size):
        self._c_bytes = chip_size  # Size of chip in bytes
        self._a_bytes = chip_size * nchips  # Size of array
        self._nbits = nbits  # Block size in bits
        self._block_size = 2**nbits

    def __len__(self):
        return self._a_bytes

    # Handle special cases of a slice. Always return a pair of positive indices.
    def do_slice(self, addr):
        if not (addr.step is None or addr.step == 1):
            raise NotImplementedError('only slices with step=1 (aka None) are supported')
        start = addr.start if addr.start is not None else 0
        stop = addr.stop if addr.stop is not None else self._a_bytes
        start = start if start >= 0 else self._a_bytes + start
        stop = stop if stop >= 0 else self._a_bytes + stop
        return start, stop

    # IOCTL protocol.
    def readblocks(self, blocknum, buf, offset=0):
        return self.readwrite(offset + (blocknum << self._nbits), buf, True)

    def writeblocks(self, blocknum, buf, offset=0):
        self.readwrite(offset + (blocknum << self._nbits), buf, False)

    def ioctl(self, op, arg):
        #print("ioctl(%d, %r)" % (op, arg))
        if op == 4:  # BP_IOCTL_SEC_COUNT
            return self._a_bytes >> self._nbits
        if op == 5:  # BP_IOCTL_SEC_SIZE
            return self._block_size
