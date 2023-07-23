#ok
import json
from sqlalchemy import create_engine, Column, Integer, String, SmallInteger, Text, CHAR, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase,  relationship

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, Session
from sqlalchemy.orm import mapped_column
import os
import fitz
from os.path import exists


DEPARTMENT_TABLE = "department"
BUNDLE_TABLE = "bundle"
DOC_TABLE = "doc"
TABLE_PREFIX = "alihmedia_inactive_"
DATABASE = "arsipdb3"
COVER_LOCATION = os.path.join("/home/farid/dev/python/Site-Django-Authentication-System", "static", "alihmedia_inactive", "cover")
PDF_LOCATION = "/home/farid/pdfs/"



engine = create_engine('mysql+pymysql://root:1234@localhost:33061/arsipdb3', echo=False)

class Base(DeclarativeBase):
    pass

class Department(Base):
    __tablename__ =  TABLE_PREFIX + DEPARTMENT_TABLE
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    defcode: Mapped[str] = mapped_column(String(20))
    link: Mapped[str] = mapped_column(String(20))

class Bundle(Base):
    __tablename__ = TABLE_PREFIX + BUNDLE_TABLE
    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey(TABLE_PREFIX + DEPARTMENT_TABLE + ".id"))
    box_number: Mapped[int] = mapped_column(SmallInteger)
    bundle_number: Mapped[int] = mapped_column(SmallInteger)
    code: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(Text)
    year: Mapped[str] = mapped_column(CHAR(4),  nullable=True)
    orinot: Mapped[str] = mapped_column(String(10), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    department = relationship("Department")


class Doc(Base):
    __tablename__ = TABLE_PREFIX + DOC_TABLE
    id: Mapped[int] = mapped_column(primary_key=True)
    bundle_id: Mapped[int] = mapped_column(ForeignKey(TABLE_PREFIX + BUNDLE_TABLE + ".id"))
    doc_number: Mapped[int] = mapped_column(SmallInteger)
    doc_count: Mapped[int] = mapped_column(SmallInteger)
    orinot: Mapped[str] = mapped_column(String(10), nullable=True)
    doc_type: Mapped[str] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    page_count: Mapped[str] = mapped_column(SmallInteger, nullable=True)
    filesize: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    bundle = relationship("Bundle")
    # comments = relationship("Comment")


def get_size(file_path, unit='bytes'):
    file_size = os.path.getsize(file_path)
    exponents_map = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3}
    if unit not in exponents_map:
        raise ValueError("Must select from \
        ['bytes', 'kb', 'mb', 'gb']")
    else:
        size = file_size / 1024 ** exponents_map[unit]
        return round(size, 3)

def get_page_count(pdffile):
    doc = fitz.open(pdffile)
    return doc.page_count

def generatecover(pdffile, coverfilename):
    path = os.path.join(COVER_LOCATION, coverfilename)
    if not exists(path):
        doc = fitz.open(pdffile)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        # output = "outfile.png"
        pix.save(path)
        doc.close()        

def main():
    Session = sessionmaker(bind = engine)
    session = Session()    
    result = session.query(Doc).join(Bundle).join(Department).all()
    for row in result:
        path = os.path.join(PDF_LOCATION, row.bundle.department.link, str(row.bundle.box_number), str(row.doc_number) + ".pdf")
        if exists(path):
            coverfilename = "{}_{}_{}.png".format(row.bundle.department.link, row.bundle.box_number, row.doc_number)
            generatecover(pdffile=path, coverfilename=coverfilename)
            filesize = get_size(path, "kb")
            pagecount = get_page_count(pdffile=path)
            session.query(Doc).filter(Doc.id == row.id).update({Doc.filesize: filesize, Doc.page_count: pagecount})
            session.commit()

if __name__ == '__main__':
    main()
