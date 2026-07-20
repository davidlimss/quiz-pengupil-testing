"""Build a results PDF from the real pytest JUnit XML and Selenium screenshots."""
import glob, os, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RImage

ROOT='artifacts'; XML=os.path.join(ROOT,'report.xml'); OUT='Laporan_Hasil_47_Testcase_David_Sam_Limbong_FINAL.pdf'
descriptions={
 'test_login_sukses':'Kredensial valid harus mengarahkan browser ke index.php.',
 'test_login_username_tidak_terdaftar':'Username tidak ada harus tetap di login dan menampilkan pesan gagal.',
 'test_login_password_salah':'Password salah harus menampilkan pesan autentikasi; saat ini ditandai XFAIL karena $error kosong.',
 'test_login_username_kosong':'Username kosong harus menampilkan pesan data tidak boleh kosong.',
 'test_login_password_kosong':'Password kosong harus menampilkan pesan data tidak boleh kosong.',
 'test_login_semua_kosong':'Kedua field kosong harus ditolak.',
 'test_login_sql_injection':'Payload SQL pada username tidak boleh membypass login.',
 'test_login_session_aktif_redirect':'Session aktif harus mengarahkan ulang ke index.php.',
 'test_login_username_dengan_spasi':'Spasi di sekitar username tidak boleh menjadi bypass.',
 'test_login_username_case_sensitive':'Perubahan kapitalisasi username harus ditolak.',
 'test_login_password_case_sensitive':'Password berbeda kapitalisasi harus ditolak.',
 'test_login_username_sangat_panjang':'Username ekstrem tidak boleh menyebabkan bypass/crash.',
 'test_login_username_markup_aman':'Markup username tidak boleh menjadi elemen HTML.',
 'test_login_refresh_mempertahankan_session':'Refresh setelah login harus mempertahankan session.',
 'test_login_membuat_cookie_session':'Login harus menghasilkan cookie PHPSESSID.',
 'test_login_submit_ulang':'Submit ulang login tidak boleh membuat masalah session.',
 'test_login_password_sql_injection':'Payload SQL pada password harus ditolak.',
}
register_names=['test_register_sukses','test_register_username_sudah_ada','test_register_password_tidak_sama','test_register_email_kosong','test_register_email_format_salah','test_register_bug_kolom_nama','test_register_xss_payload_nama','test_register_password_pendek','test_register_password_panjang','test_register_nama_unicode','test_register_username_sql_injection','test_register_email_sql_injection','test_register_username_xss_aman','test_register_nama_apostrof','test_register_username_spasi','test_register_session_aktif_redirect','test_register_password_tersimpan_hash','test_register_email_duplikat','test_register_email_sangat_panjang','test_register_username_sangat_panjang','test_register_submit_post','test_register_refresh_tidak_duplikat','test_register_nama_markup','test_register_nama_hanya_spasi','test_register_email_case','test_register_username_case_duplikat','test_register_repassword_spasi','test_register_tepat_satu_baris','test_register_name_bukan_default','test_register_csrf_token_dicatat']
register_desc=['Data valid membuat user dan redirect.','Username duplikat harus ditolak.','Password dan re-password berbeda harus ditolak.','Email kosong harus ditolak.','Email invalid harus ditolak server; saat ini bug validasi.','Kolom name harus berisi input; saat ini bug $nama vs $name.','Payload XSS pada nama tidak boleh dieksekusi.','Password pendek harus ditolak; validasi belum ada.','Password panjang harus diproses.','Nama Unicode harus tersimpan.','SQL injection username diperlakukan sebagai teks.','SQL injection email diperlakukan sebagai teks.','Payload XSS username tidak boleh dieksekusi.','Apostrophe nama tidak boleh merusak query.','Spasi username diuji konsistensinya.','Session aktif seharusnya redirect; guard memakai key salah.','Password database harus bcrypt/hash.','Email duplikat diuji sebagai kebijakan.','Email ekstrem harus ditangani aman.','Username ekstrem harus ditangani aman.','Form harus terkirim dengan POST.','Refresh tidak boleh insert ulang.','Markup nama diperlakukan sebagai teks.','Nama hanya spasi harus ditolak.','Email kapital harus diproses konsisten.','Username beda kapital diuji.','Re-password dengan spasi harus ditolak.','Satu registrasi menghasilkan satu baris.','Nilai name harus berasal dari input; bug terkonfirmasi.','Form perlu token CSRF; saat ini menjadi risiko security.' ]
descriptions.update(dict(zip(register_names,register_desc)))
root=ET.parse(XML).getroot(); results=[]
for node in root.findall('.//testcase'):
 name=node.attrib['name']; status='XFAIL' if node.find('skipped') is not None else 'FAIL' if node.find('failure') is not None or node.find('error') is not None else 'PASS'
 note=descriptions.get(name,'Skenario Selenium UI dan assertion database.')
 failure=node.find('failure')
 if failure is None: failure=node.find('error')
 if failure is not None and failure.attrib.get('message'):
  note += ' Aktual: '+failure.attrib['message'].splitlines()[0][:180]
 results.append((name,status,note))

# Contact sheets make the actual browser evidence readable without creating 47 huge pages.
paths=sorted(glob.glob(os.path.join(ROOT,'*.png'))); sheets=[]
for start in range(0,len(paths),6):
 chunk=paths[start:start+6]; sheet=Image.new('RGB',(1200,900),'white'); draw=ImageDraw.Draw(sheet)
 for j,path in enumerate(chunk):
  im=Image.open(path).convert('RGB'); im.thumbnail((380,390)); x=(j%3)*400; y=(j//3)*450; sheet.paste(im,(x,y+25)); draw.text((x,y),os.path.basename(path)[:48],fill='black')
 out=os.path.join(ROOT,f'contact_{start//6+1}.jpg'); sheet.save(out,quality=85); sheets.append(out)

styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name='Tiny',parent=styles['BodyText'],fontSize=7,leading=8)); doc=SimpleDocTemplate(OUT,pagesize=A4,rightMargin=10*mm,leftMargin=10*mm,topMargin=10*mm,bottomMargin=10*mm)
story=[Paragraph('LAPORAN HASIL PENGUJIAN LOGIN & REGISTER',styles['Title']),Paragraph('David Sam Limbong | III RPLK | 2322101894',styles['Normal']),Paragraph('Aplikasi quiz-pengupil — hasil diambil dari artifacts/report.xml',styles['Normal']),Spacer(1,8)]
story += [Paragraph('Ringkasan Eksekusi',styles['Heading2']),Paragraph(f'Total: {len(results)} testcase. PASS: {sum(s=="PASS" for _,s,_ in results)}; XFAIL: {sum(s=="XFAIL" for _,s,_ in results)}; FAIL: {sum(s=="FAIL" for _,s,_ in results)}. XFAIL berarti bug yang sengaja dikonfirmasi, sedangkan FAIL berarti assertion aktual belum memenuhi ekspektasi.',styles['BodyText']),Spacer(1,6)]
rows=[['ID','Testcase','Status','Penjelasan']]
login_no=register_no=0
for name,status,desc in results:
 if 'login' in name: login_no+=1; ident=f'LG-{login_no:02}'
 else: register_no+=1; ident=f'RG-{register_no:02}'
 rows.append([ident,name.replace('test_',''),status,desc])
t=Table([[Paragraph(str(x),styles['Tiny']) for x in r] for r in rows],colWidths=[15*mm,48*mm,17*mm,105*mm],repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),('TEXTCOLOR',(0,0),(-1,-1),colors.black),('GRID',(0,0),(-1,-1),.35,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')]))
story += [Paragraph('Rincian Hasil Setiap Testcase',styles['Heading2']),t,PageBreak(),Paragraph('Bukti Screenshot Browser',styles['Heading2']),Paragraph('Setiap screenshot ditampilkan satu per halaman dengan ukuran besar agar pesan dan field dapat dibaca jelas.',styles['BodyText'])]
for path in paths:
 im=Image.open(path); w,h=im.size; maxw=185*mm; maxh=235*mm; scale=min(maxw/w,maxh/h)
 story += [Spacer(1,6),Paragraph(os.path.basename(path),styles['Heading3']),RImage(path,width=w*scale,height=h*scale),PageBreak()]
story += [PageBreak(),Paragraph('Temuan Utama',styles['Heading2']),Paragraph('1) Password salah pada login tidak mengisi $error. 2) Register memakai $nama alih-alih $name. 3) Format email dan panjang password belum divalidasi server. 4) Guard session register memeriksa user bukan username. 5) Output input belum di-escape sehingga berisiko XSS. Temuan ini tercermin pada status XFAIL/FAIL dan screenshot.',styles['BodyText']),Paragraph('Repository sumber: https://github.com/hermanka/quiz-pengupil',styles['BodyText'])]
doc.build(story); print(OUT)
