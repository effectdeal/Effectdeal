from .calculations import report_totals

def seed(store, tenant):
    datasets = {
      'employees': [
        {'id':'owner','name':'Majitel EFFECT DEAL','email':'owner@example.cz','role':'owner','hourlyRate':0,'available':True},
        {'id':'dispatcher','name':'Petra Svobodová','email':'dispatcher@example.cz','role':'dispatcher','hourlyRate':0,'available':True},
        {'id':'driver','name':'Jan Novák','email':'driver@example.cz','role':'employee','hourlyRate':0,'available':True},
      ],
      'vehicles': [
        {'id':'octavia','brand':'Škoda','model':'Octavia','plate':'1AB 2345','vin':'TMBDEMO0000000001','year':2023,'color':'Šedá','drive':'Přední','fuel':'Nafta','transmission':'Automatická','power':110,'equipment':'Tempomat, klimatizace, parkovací kamera','description':'Ukázkové vozidlo.','status':'available','monthlyPrice':24900,'location':'Brno','latitude':49.1951,'longitude':16.6068,'odometer':42000,'defects':'Bez zjištěných závad','lastRentalEnd':'2026-10-28'},
        {'id':'transporter','brand':'Volkswagen','model':'Transporter','plate':'2BC 4567','vin':'WV1DEMO0000000002','year':2022,'color':'Bílá','drive':'Přední','fuel':'Nafta','transmission':'Manuální','power':110,'equipment':'Klimatizace, tažné zařízení','description':'Ukázkové vozidlo.','status':'available','monthlyPrice':29900,'location':'Praha','latitude':50.0755,'longitude':14.4378,'odometer':68000,'defects':'Drobný škrábanec nárazníku','lastRentalEnd':''},
      ],
      'customers':[{'id':'customer-demo','name':'Ukázkový zákazník','type':'company','email':'customer@example.cz','phone':'','address':'Praha Říčany','companyId':''}],
      'rentals':[{'id':'rental-demo','customerId':'customer-demo','vehicleId':'octavia','start':'2026-10-29','end':'2026-11-29','monthlyPrice':24900,'deposit':10000,'status':'reserved','note':'Ukázkový měsíční pronájem'}],
      'transfers':[{'id':'transfer-demo','rentalId':'rental-demo','customerId':'customer-demo','vehicleId':'octavia','employeeId':'driver','from':'Brno','to':'Praha Říčany','date':'2026-10-29','time':'10:00','status':'assigned','type':'delivery','note':'Převzít vůz a předat zákazníkovi.','reportId':'report-transfer-demo'}],
      'reports':[{'id':'report-transfer-demo','employeeId':'driver','transferId':'transfer-demo','vehicleId':'octavia','title':'Převoz Octavie · Praha → Brno → Praha','status':'draft','hourlyRate':0,'weekendBonus':0,'holidayBonus':0,'reward':0,'overtimeMinutes':0,'completedTasks':1,'note':'Ukázka pracovního výkazu','legs':[{'date':'2026-10-29','from':'Praha','to':'Brno','method':'Vlak','purpose':'Vyzvednutí vozidla','startTime':'07:00','endTime':'10:00','minutes':180,'breakMinutes':0,'km':205,'tickets':420},{'date':'2026-10-29','from':'Brno','to':'Praha Říčany','method':'Převážené vozidlo','purpose':'Předání zákazníkovi','startTime':'10:00','endTime':'13:30','minutes':210,'breakMinutes':0,'km':205}]}],
      'notifications':[], 'handover':[], 'documents':[], 'service':[], 'invoices':[], 'payments':[],
    }
    for kind, rows in datasets.items():
        for row in rows:
            if kind == 'reports': row['totals'] = report_totals(row, 0)
            if not store.get(tenant,kind,row['id']):
                store.create(tenant,kind,row)
