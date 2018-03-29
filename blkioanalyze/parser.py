from struct import unpack
from collections import namedtuple

class BlkBinaryParser(object):
    """
    This class parses a blkparse binary file file format which made of
    a set of records with the following format:

    struct blk_io_trace {
            __u32 magic;		/* MAGIC << 8 | version */
            __u32 sequence;		/* event number */
            __u64 time;		/* in nanoseconds */
            __u64 sector;		/* disk offset */
            __u32 bytes;		/* transfer length */
            __u32 action;		/* what happened */
            __u32 pid;		/* who did it */
            __u32 device;		/* device identifier (dev_t) */
            __u32 cpu;		/* on what cpu did it happen */
            __u16 error;		/* completion error */
            __u16 pdu_len;		/* length of data after this trace */
    };

    It filters action by three possible states "Q", "D", "C".
    All other actions are rejected.
    """

    # data shared among all instances
    # actions that will be saved in output stream
    blk_action = {'Q':1, 'D':7, 'C':8}
    blk_reverse_action = {1: 'Q', 7: 'D', 8: 'C'}
    # Binary format for unpacking blk_io_trace structure
    # from C to python
    blk_io_trace_fmt = "@IIQQIIIIIHH"
    # fixed part of the record size in bytes (variable part is defined by 'pdu_len' field
    record_size = 48
    # initial record format
    BlkIOTrace = namedtuple('BlkIOTrace', 'magic sequence time sector bytes action pid device cpu error pdu_len')
    # transformed record format with removed 'magic' and variable part and reordered fields
    BlkIOTraceTransformed = namedtuple('BlkIOTraceTransformed', 'time sequence sector bytes action pid cpu error')

    def __init__(self, filename):
        self.f = open(filename, "rb")
        self.result = []

    def __transform(self, blk_io_trace, masked_action, **kwargs):
        """
        Transforms data from the initial blkparse format to the more
        convenient format
        """
        # Transform action from a digit to letter
        action = __class__.blk_reverse_action[masked_action]

        transformed = __class__.BlkIOTraceTransformed(
            blk_io_trace.time,
            blk_io_trace.sequence,
            blk_io_trace.sector,
            blk_io_trace.bytes,
            action,
            blk_io_trace.pid,
            blk_io_trace.cpu,
            blk_io_trace.error,
        )

        return transformed

    def parse(self, **kwargs):
        """
        Parse the input file and return a set of BlkIOTraceTransformed
        records
        """
        with self.f as f:
            blk_data = f.read(__class__.record_size)
            while len(blk_data) == __class__.record_size:
                # get fixed record
                blk_io_trace = __class__.BlkIOTrace._make(unpack(__class__.blk_io_trace_fmt, blk_data))

                # skip variable length part
                if blk_io_trace.pdu_len:
                    f.seek(blk_io_trace.pdu_len, 1)

                # mask action to remove unneded info and add
                # records with actions 'Q', 'D' and 'C' to the
                # output stream
                action = blk_io_trace.action & 0xffff
                if action in __class__.blk_action.values():
                    self.result.append(self.__transform(blk_io_trace, action))

                # get next record
                blk_data = f.read(__class__.record_size)

        return self.result
