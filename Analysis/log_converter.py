"""
Handles the parsing of MAVLink .tlog files.
"""

import csv
from pymavlink import mavutil
from . import config # <-- MODIFIED: Relative import

class TlogParser:
    def __init__(self, log_file, dialect=config.DEFAULT_DIALECT):
        self.log_file = str(log_file)
        self.mlog = mavutil.mavlink_connection(self.log_file, dialect=dialect)
        self.fields = config.FORENSIC_FIELDS 
        self.type_set = set(self.fields) 
        self.csv_fields = ['timestamp']
        nan = float('nan')
        self.data = [nan]
        self.offsets = {}

        for type_, field_list in self.fields.items():
            self.offsets[type_] = len(self.csv_fields)
            self.csv_fields.extend(f'{type_}.{attr}' for attr in field_list)
            self.data.extend(nan for _ in range(len(field_list)))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.mlog.close()

    def __iter__(self):
        while msg := self.mlog.recv_match(type=self.type_set):
            if msg.get_type() == 'BAD_DATA': continue
            yield msg

    def _update(self, type_, data_dict):
        offset = self.offsets[type_]
        for index, desired_attr in enumerate(self.fields[type_]):
            self.data[offset+index] = data_dict.get(desired_attr, float('nan'))

    def process_log(self):
        last_timestamp = None
        with self as mavlink:
            for msg in mavlink:
                yielded_last_row = False
                timestamp = getattr(msg, '_timestamp', 0.0)
                data_dict = msg.to_dict()

                if last_timestamp is not None and timestamp != last_timestamp:
                    self.data[0] = f'{last_timestamp:.8f}'
                    yield self.data
                    yielded_last_row = True

                self._update(msg.get_type(), data_dict)
                last_timestamp = timestamp

            if not yielded_last_row and last_timestamp is not None:
                self.data[0] = f'{last_timestamp:.8f}'
                yield self.data

    def to_csv(self, output_file):
        print(f"Processing {self.log_file}...")
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_fields)
                for data_row in self.process_log():
                    writer.writerow([str(val) for val in data_row])
            print(f"Success: Forensic CSV saved to {output_file}")
            return True
        except Exception as e:
            print(f"CSV Error: {e}")
            return False