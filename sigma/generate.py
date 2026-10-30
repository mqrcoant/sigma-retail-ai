import sqlite3, random, datetime, pathlib
from decimal import Decimal
ROOT=pathlib.Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'sigmaretail.sqlite'
SCHEMA=(ROOT/'sql'/'01_schema.sql').read_text(encoding='utf8')
def build():
 DB.parent.mkdir(exist_ok=True)
 if DB.exists():DB.unlink()
 c=sqlite3.connect(DB);c.execute('PRAGMA foreign_keys=ON');c.executescript(SCHEMA)
 random.seed(42026)
 products=[('Portátil Pro','Informática',1099,720),('Portátil Basic','Informática',589,355),('Monitor 27','Informática',259,151),('Mouse','Accesorios',25,9),('Teclado','Accesorios',49,18),('Auriculares','Audio',89,39),('Altavoz','Audio',139,65),('TV 55','Televisores',680,445),('TV 43','Televisores',389,251),('Tablet','Móviles',349,208),('Smartphone X','Móviles',799,509),('Cargador','Accesorios',29,11)]
 c.executemany('INSERT INTO dim_producto(producto_sk,nombre,categoria,precio_lista,costo_unitario) VALUES(?,?,?,?,?)',[(i+1,*p) for i,p in enumerate(products)])
 for i,name in enumerate(['Madrid Centro','Lugo','A Coruña','Santiago'],1):c.execute('INSERT INTO dim_sucursal VALUES(?,?)',(i,name))
 for i,name in enumerate(['Tienda','Web','Marketplace'],1):c.execute('INSERT INTO dim_canal VALUES(?,?)',(i,name))
 c.executemany('INSERT INTO dim_promocion VALUES(?,?)',[(1,'Sin promoción'),(2,'Campaña'),(3,'Fidelización')])
 # 60 clientes; primeros diez cambian de segmento el 2026-07-01 y mantienen historia SCD2.
 for i in range(1,61):
  old=['Minorista','Empresa','Premium'][(i-1)%3]
  c.execute('INSERT INTO dim_cliente VALUES(?,?,?,?,?,?)',(i,i,'Cliente %03d'%i,old,'2026-01-01','2026-06-30' if i<=10 else '9999-12-31'))
  if i<=10:c.execute('INSERT INTO dim_cliente VALUES(?,?,?,?,?,?)',(60+i,i,'Cliente %03d'%i,'Premium' if old!='Premium' else 'Minorista','2026-07-01','9999-12-31'))
 dates=[datetime.date(2026,1,1)+datetime.timedelta(days=i) for i in range(365)]
 c.executemany('INSERT INTO dim_tiempo VALUES(?,?,?,?,?,?)',[(int(d.strftime('%Y%m%d')),d.isoformat(),d.year,d.month,(d.month-1)//3+1,d.strftime('%Y-%m')) for d in dates])
 lines=[];ticket=0;source_gross=source_discounts=source_refunds=source_cost=0
 for month in range(1,13):
  for j in range(85):
   ticket+=1;day=random.randint(1,28);dt=datetime.date(2026,month,day);date_sk=int(dt.strftime('%Y%m%d'))
   natural=random.randint(1,60);client_sk=natural+60 if natural<=10 and month>=7 else natural
   branch=random.randint(1,4);channel=random.choices([1,2,3],[.5,.35,.15])[0];promo=random.randint(1,3)
   for k in range(random.randint(1,3)):
    p=random.randint(1,len(products));q=random.randint(1,4);price=products[p-1][2];cost=products[p-1][3]
    gross=q*price*100;discount=(gross* ([0,5,10][promo-1]))//100
    # net refunds represented explicitly, allowing negative-margin edge cases
    refund=(gross-discount) if random.random()<.015 else 0
    costo=q*cost*100 if not refund else 0
    net=gross-discount-refund;margin=net-costo
    lines.append((ticket,k+1,date_sk,p,client_sk,branch,channel,promo,q,gross,discount,refund,net,costo,margin))
    source_gross+=gross;source_discounts+=discount;source_refunds+=refund;source_cost+=costo
 c.executemany('INSERT INTO fact_ventas(ticket_id,linea_nro,tiempo_sk,producto_sk,cliente_sk,sucursal_sk,canal_sk,promocion_sk,cantidad,ingreso_bruto_cent,descuento_cent,devolucion_cent,ingreso_neto_cent,costo_cent,margen_bruto_cent) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',lines)
 c.execute('INSERT INTO conciliacion_fuente VALUES(?,?,?,?,?,?)',(len(lines),source_gross,source_discounts,source_refunds,source_cost,source_gross-source_discounts-source_refunds))
 c.commit();c.close()
 return {'tickets':ticket,'lineas':len(lines),'db':str(DB)}
if __name__=='__main__':print(build())
