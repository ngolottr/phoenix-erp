import fitz

doc = fitz.open(r"C:\Users\nicolas.golott\Desktop\PROYECTO PHOENIX ERP\cotizacion_sap.pdf")
lineas = doc[0].get_text().split('\n')
for i, l in enumerate(lineas):
    print(i, repr(l))
doc.close()
