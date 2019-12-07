from flask import Flask, render_template, session, request
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Leyno'

conn = pymysql.connect(host='tsuts.tskoli.is', port=3306, user='2210022020', password='borkur66', database='2210022020_lokaverkefni')
# https://pythonspot.com/login-authentication-with-flask/

cur = conn.cursor()
cur.execute("SELECT products.product_id, products.product, products.price, stock.amount, myndir.nafn from products inner join stock on products.product_id = stock.product_id inner join myndir on products.product_id = myndir.product_id")
vorur = cur.fetchall()

@app.route('/')
def index():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    p = cur.fetchall()

    if 'logged_in' not in session:
        session['logged_in'] = []

    for i in p:
        print(session['logged_in'])
        if i[3] in session['logged_in']:
            nafn = i[3]
            karfa = 0
            if 'karfa' in session:
                karfa = len(session['karfa'])
                til = True
            else:
                til = False
            return render_template("index.html", p=p, n=nafn, vorur=vorur, k=karfa, til=til)
        else: 
            return render_template("login.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        e = request.form['email']
        p = request.form['password']
    
    cur = conn.cursor()
    cur.execute("SELECT count(user) FROM users where email = %s and pass=%s",(e,p))
    p = cur.fetchone()
    if p[0] == 1:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        f = cur.fetchall()

        session['logged_in'] = f[0][3]
        return render_template("rett.html")
    else:
        return render_template("rangt.html")

@app.route('/nyskra')
def nyskra():
    return render_template("nyskra.html")

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        e = request.form['email']
        n = request.form['notandanafn']
        pw = request.form['password']
        nafn = request.form['nafn']

        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM users where user = %s",(n))
        p = cur.fetchone()
        if p[0] != 1:
            cur.execute("INSERT INTO users(email,user,pass,nafn) VALUES(%s,%s,%s,%s)",(e,n,pw,nafn))
            conn.commit()
            cur.close()
            return render_template("nyr.html")

        else:
            return render_template("tekid.html")

@app.route('/utskra')
def utskra():
    session.pop('logged_in',None)

    return render_template("utskra.html")

@app.route('/vefur')
def vefur():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    p = cur.fetchall()
    for i in p:
        if i[0] in session['logged_in']:
            nafn = i[2]
        
    return render_template("vefur.html", p=p, n=nafn)

#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

@app.route('/ikorfu/<int:id>')
def ikorfu(id):
	karfa = []
	if 'karfa' in session:
		karfa = session['karfa']
		karfa.append(id)
		session['karfa'] = karfa
	else:
		karfa.append(id)
		session['karfa'] = karfa
	print(len(karfa))
	return render_template("ikorfu.html", vorur=vorur)

@app.route('/karfa')
def karfa():
	karfa = []
	k=0
	heild=0
	if 'karfa' in session:
		karfa = session['karfa']
		k = len(session['karfa'])
		for x in karfa:
			for y in vorur:
				if y[0] == x:
					heild += y[2]
	return render_template("karfa.html", vorur=vorur, karfa=karfa, k=k, heild=heild)


@app.route('/eyda/<int:id>')
def eyda(id):
	karfa = []
	if 'karfa' in session:
		karfa = session['karfa']
		karfa.remove(id)
		session['karfa'] = karfa
	return render_template("eyda.html", vorur=vorur)

@app.route('/taema')
def taema():
	session.pop('karfa',None)
	return render_template("taema.html", vorur=vorur)

@app.route('/karfa/kaupa')
def kaupa():
	karfa = []
	heild = 0
	if 'karfa' in session:
		karfa = session['karfa']
		for x in karfa:
			for y in vorur:
				if y[0] == x:
					heild += y[2]
	return render_template("kaupa.html", vorur=vorur, karfa=karfa, heild=heild)

@app.route('/karfa/kaupa/takk', methods=['GET','POST'])
def takk():
    for vara in session['karfa']:
        if vara[3] > 0:
            cur = conn.cursor()
            cur.execute("UPDATE stock SET amount = amount - 1 WHERE product_id = vara and amount > 0")
        else:
            return render_template("uppselt.html", vara=vara)

	karfa = []
	session['karfa'] = karfa
    
	return render_template("takk.html", vorur=vorur, nafn=nafn, netfang=netfang)


@app.errorhandler(404)
def error404(error):
	return "Síða ekki fundin", 404

if __name__ == '__main__':
    app.run(debug=True)