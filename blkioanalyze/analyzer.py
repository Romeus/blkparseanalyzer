import pandas as pd
from blkioanalyze import parser

class BlkIOAnalyzer(object):
    """
    Reads blkparse binary file format, parse it using BlkBinaryParser
    and calculate varioius statistics using pandas
    """
    def __init__(self, filename):
        result = pd.DataFrame(parser.BlkBinaryParser(filename).parse())

        # Drop the first line which is a header
        result.drop(0, inplace=True)

        # Add require statistics columns to the queryset
        result['q2c'], result['d2c'], result['os_overhead'] = [0, 0, 0]

        # There are three records for each sector in the source queryset
        # that placed in the following order: 'Q', 'D', 'C'. The only
        # distinction between them is the 'action' field value.
        # We don't need to have all three recodrs types for each sector.
        # We need to calculate q2c, d2c and os_overhead fields and populate
        # with their values only one of the records (I have chosen 'Q' type).
        # Other two records will be filtered out.
        for i in range(1, int(len(result)), 3):
            q_row = result.loc[i]
            d_row = result.loc[i+1]
            c_row = result.loc[i+2]

            q2c = c_row.time - q_row.time
            d2c = c_row.time - d_row.time
            os_overhead = q2c/d2c

            result.loc[i, 'q2c'] = q2c
            result.loc[i, 'd2c'] = d2c
            result.loc[i, 'os_overhead'] = os_overhead

        # Remove redudant sector's records using the fact that
        # for those records colums 'q2c', 'd2c', 'os_overhead'
        # will be 0. So it doesn't matter which of the three columns
        # use to filter
        self.result = result[result['q2c'] > 0]

    def __get_sectors_count(self, x):
        num_reads = len(x)
        sector = x.sector.iloc[0]
        return pd.Series([sector, num_reads], index=['sector', 'num_reads'])

    def get_result(self):
        return self.result

    def get_average_device_response_time(self):
        return self.result['d2c'].mean()

    def get_maximum_device_response_time(self):
        return self.result['d2c'].max()

    def get_minimal_device_response_time(self):
        return self.result['d2c'].min()

    def get_os_overhead(self):
        return self.result['os_overhead'].tolist()

    def get_sectors_statistics(self):
        return self.result.groupby('sector').apply(self.__get_sectors_count)

    def get_sector_reads(self):
        return self.result['sector']
