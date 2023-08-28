import tarfile
import os.path
from settings import *
import datetime
def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def main():
    datenow = datetime.datetime.now().strftime("%Y%m%d")
    fname = "backup_{}.tar.gz".format(datenow)
    make_tarfile(os.path.join(BACKUP_LOCATION, fname), PDF_LOCATION)

if __name__ == '__main__':
    main()
