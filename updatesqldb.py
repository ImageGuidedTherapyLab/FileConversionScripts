import sqlite3
import time
import dicom
conn = sqlite3.connect('/data/fuentes/DICOM/ctkDICOM.sql')
# 
# drop table dicom_header; 
# delete from dicom_header; 
#conn.execute('create table if not exists dicom_header (SOPInstanceUID varchar(64) not null, dicomkey varchar(32) not null ,name varchar(64), value varchar(512), primary key (SOPInstanceUID,dicomkey) )')
conn.execute('create table if not exists dicom_header (SeriesInstanceUID VARCHAR(64) NOT NULL , dicomkey varchar(32) not null ,name varchar(64), value varchar(512), PRIMARY KEY (SeriesInstanceUID,dicomkey) )' )
conn.execute("DROP view IF EXISTS 'echotime'         ")
conn.execute("DROP view IF EXISTS 'reptime'          ")
conn.execute("DROP view IF EXISTS 'studydate'        ")
conn.execute("DROP view IF EXISTS 'seriedescription' ")
conn.execute('create view echotime         as select * from dicom_header where dicomkey = "(0018, 0081)" ')
conn.execute('create view reptime          as select * from dicom_header where dicomkey = "(0018, 0080)" ')
conn.execute('create view studydate        as select * from dicom_header where dicomkey = "(0008, 0020)" ')
conn.execute('create view seriedescription as select * from dicom_header where dicomkey = "(0008, 103e)" ')

#fileIDList = [ (seriesUID,filename) for (seriesUID,filename) in conn.execute('select SeriesInstanceUID,Filename from Images limit 5')]

# only update files that are "DaysBackOld"
DaysBack = 2;
# convert all to seconds
# 60 sec * 60 min * 24hr = number of secs in day
datecutoff = time.strftime("%Y-%m-%d",time.localtime(time.time() - 60.*60.*24.*DaysBack )) 
# select by modality and date
fileIDList = [ (seriesUID,filename) for (seriesUID,filename) in conn.execute('select im.SeriesInstanceUID,im.Filename from Images im join Series se on im.SeriesInstanceUID=se.SeriesInstanceUID where DateTime(im.InsertTimeStamp) > "%s" and se.Modality like "%%mr%%" ' % datecutoff )]


#print fileIDList
#
errlogfileHandle = file('err.txt'  ,'w')
for (seriesUID,filename) in fileIDList:
  print 'Processing %s' % filename
  dcm=dicom.read_file(filename);
  # remove problem keys
  problemkeylist = [(0x7fe0,0x0010),(0x0043,0x1095),(0x0043,0x1028),(0x0043,0x1029),(0x0043,0x102a),(0x0025,0x101b),(0x0028,0x0107)]
  keylist = [dcmkey for dcmkey in dcm.keys() if dcmkey not in problemkeylist ]
  for dcmkey in keylist :
      try: 
        # catch key exceptions
        name=dcm[dcmkey].name;
        value=dcm[dcmkey].value;
        # insert and ignore duplicate entries
        tableentry=(unicode(str(seriesUID)),unicode(str(dcmkey)),unicode(str(name)),unicode(str(value)))
        conn.execute('insert or ignore into dicom_header (SeriesInstanceUID,dicomkey,name,value) values (?,?,?,?)' , tableentry)
      ## except sqlite3.IntegrityError as inst:
      ## except UnicodeDecodeError as inst:
      ## except ValueError as inst:
      # catch key exceptions
      except Exception as inst:
        errlogfileHandle.write("%s," % inst )
        errlogfileHandle.write('%s,%s\n' %  ( unicode(str(seriesUID)),unicode(str(dcmkey)) ) )
      finally:
        # this is always executed
        errlogfileHandle.flush()
  conn.commit()

errlogfileHandle.close()


## USEFUL COMMANDS
## ---------------
## select count(*) from dicom_header where Name="Slice Thickness" and cast(value as number)<2;
## select value from dicom_header where name="Slice Thickness" group by value order by value;
## select im.SeriesInstanceUID,se.SeriesDescription,h.value from dicom_header h join Images im on im.SOPInstanceUID=h.SOPInstanceUID join Series se on se.SeriesInstanceUID=im.SeriesInstanceUID where h.Name="Slice Thickness" and cast(h.value as number)<=2 group by im.SeriesInstanceUID;

## DROP view IF EXISTS 'tmpsubset' ;
## create view tmpsubset as select * from dicom_header where value = 012345 and name = "Patient ID" ; 
## select sb.name,sb.value,hd.name,hd.value,im.SeriesInstanceUID,im.Filename from dicom_header hd join tmpsubset sb on sb.SOPInstanceUID=hd.SOPInstanceUID join Images im on hd.SOPInstanceUID=im.SOPInstanceUID where hd.Name like "%slice%" and cast(hd.value as number) <=3 ; 

## drop view WS_PACS;
## create view WS_PACS as select st.StudyInstanceUID,se.SeriesInstanceUID,im.FileName from images im join Series se on se.SeriesInstanceUID=im.SeriesInstanceUID join Studies st on st.StudyInstanceUID=se.StudyInstanceUID;

## sqlite> select sr.SeriesDescription,hd.value from series sr join Images im on sr.SeriesInstanceUID = im.SeriesInstanceUID join dicom_header hd on im.SOPInstanceUID = hd.SOPInstanceUID where sr.SeriesDescription like '%ax%' and  hd.dicomkey = '(0020, 0037)' limit 4;
## sqlite> select sr.SeriesDescription,hd.value from series sr join Images im on sr.SeriesInstanceUID = im.SeriesInstanceUID join dicom_header hd on im.SOPInstanceUID = hd.SOPInstanceUID where sr.SeriesDescription like '%sag%' and  hd.dicomkey = '(0020, 0037)' limit 4;
## sqlite> select sr.SeriesDescription,hd.value from series sr join Images im on sr.SeriesInstanceUID = im.SeriesInstanceUID join dicom_header hd on im.SOPInstanceUID = hd.SOPInstanceUID where sr.SeriesDescription like '%cor%' and  hd.dicomkey = '(0020, 0037)' limit 4;

# select hd.value,tr.name,tr.value,te.name,te.value from dicom_header hd join echotime te on te.SeriesInstanceUID=hd.SeriesInstanceUID join reptime tr on hd.SeriesInstanceUID=tr.SeriesInstanceUID where hd.value like '%T1%' or hd.value like '%T2%' ;

