import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import sys
import argparse
import os
from numpy import mean as np_mean


def main():
    # Handle the arguments
    parser = argparse.ArgumentParser(prog=os.path.basename(
        sys.argv[0]), description='Glucose plotter')
    parser.add_argument('--input-file', '-if', metavar=None,
                        type=str, help='Glucose data file in CSV')
    parser.add_argument('--output-file', '-of', type=str,
                        help='Glucose graph in png')
    parser.add_argument('--ingest', action='store',
                        default=False, help='Plot ingests as vertical lines')
    args = parser.parse_args()

    datafile = args.input_file

    if datafile is None:
        print('Please, provide a datafile\n')
        exit(1)

    if args.output_file is None:
        output_file = datafile[:-4] + '_' + \
            datetime.now().strftime("%d%m%y%H%M") + '.png'
    else:
        output_file = args.output_file

    print('Parsing file: {}'.format(datafile))
    file_text = None
    with open(datafile, 'r') as f:
        file_text = f.read()

    measure_re = re.compile(r'(\d+-\d+-\d+ \d+:\d+),[01]\,+(\d+\.\d+)')
    ingest_re = re.compile(r'(\d+-\d+-\d+ \d+:\d+),5\,+(\d+)')

    measure_data = measure_re.findall(file_text)
    ingest_data = ingest_re.findall(file_text)

    gluc_timestamp_array = []
    glucose_array = []
    for date, glucose in measure_data:
        gluc_timestamp_array.append(datetime.strptime(date, "%d-%m-%Y %H:%M"))
        glucose_array.append(float(glucose))
    print('Data file contains: {} measurements'.format(len(gluc_timestamp_array)))

    ingest_timestamp_array = []
    ingest_array = []
    for date, ingest in ingest_data:
        ingest_timestamp_array.append(
            datetime.strptime(date, "%d-%m-%Y %H:%M"))
        ingest_array.append(float(ingest))

    (gluc_timestamp, glucose) = zip(
        *sorted(zip(gluc_timestamp_array, glucose_array)))
    (ingest_timestamp, ingest) = zip(
        *sorted(zip(ingest_timestamp_array, ingest_array)))

    fig, ax = plt.subplots(figsize=(40, 10))

    ax.plot(gluc_timestamp, glucose)

    if args.ingest:
        for idx in range(len(ingest)):
            plt.axvline(ingest_timestamp[idx], linestyle='--', color='red')
            plt.annotate('{} g'.format(ingest[idx]), (ingest_timestamp[idx], np_mean(glucose)*5/6),
                         textcoords="offset points", xytext=(40, 10), ha='center', size=20)

    plt.xlabel('Time')
    plt.ylabel('glucose mmol/l')
    plt.gcf().autofmt_xdate()
    plt.grid(color='gray', linestyle='-', linewidth=1)
    ax.xaxis_date()
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    plt.tight_layout()
    print('Exporting plot to: {}'.format(output_file))
    plt.savefig(output_file)


if __name__ == "__main__":
    sys.exit(main())
