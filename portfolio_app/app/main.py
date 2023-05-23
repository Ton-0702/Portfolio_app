from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask import json
import mysql.connector
import re
import pandas as pd
from sql_cur import sql_cursor

app = Flask(__name__)
app.config["SECRET_KEY"] = "luathieng2"

mydb = mysql.connector.connect(
            host="localhost",
            port ="3307",
            user="root",
            password="toan123",
            database="LOGIN"
        )
mydb.time_zone = "+7:00"

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == "POST" and 'email_login' in request.form and 'pw_login' in request.form:
        # Create variables for easy access
        user_email = request.form['email_login']
        user_pw  = request.form['pw_login']
        # print(user_email)
        # Check if form exists using MySQL
        cur = mydb.cursor()
        
        # Fetch one record and return result
        accounts = sql_cursor.check_login(cur, user_email, user_pw)
        # print('not ok')
        # If account exists in form table in our database
        if accounts:
            # print('ok')
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['account_id'] = accounts[0]
            session['email_login'] = accounts[1]
            session['pw'] = accounts[2]
            session['name'] = accounts[3]
            session['address'] = accounts[4]
            session['national_id'] = accounts[5]
            session['phone'] = accounts[6]
            session['date_of_birth'] = accounts[7]
            session['cash_amount'] = accounts[8]
            # Redirect to home page
            # print('ok2')
            return redirect(url_for('home_iuh_invest'))
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect user email/password!')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_acc():
    # return render_template('register_acc.html')
    
    if request.method == "POST" and 'email' in request.form and 'pw' in request.form and 'passport' in request.form: #and 'passport' in request.form:
        details = request.form
        user_email = details['email']
        user_name = details['name']
        user_cccd = details['passport']
        user_address = details['address']
        user_phone = details['phone']
        user_date = details['date']
        user_pw = details['pw']
        # Check if account exists using MySQL
        cur = mydb.cursor()
        cur.execute('SELECT * FROM account WHERE email = %s', (user_email,))
        accounts = cur.fetchone()
        # If accounts exists show error and validation checks
        if accounts:
            msg = 'Email already exists!'
            return render_template('register_acc.html', msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', user_email):
            msg = 'Invalid email address!'
            return render_template('register_acc.html', msg=msg)
        elif not re.match(r'^(\d{9}|\d{12})$', user_cccd):
            msg = 'CCCD/CMND 9 or 12 numbers'
            return render_template('register_acc.html', msg=msg)
        elif not re.match(r'^(\d{10})$', user_phone):
            msg = 'Phone must 10 numbers'
            return render_template('register_acc.html', msg=msg)
        else:
            check1= True

        cur.execute('SELECT * FROM account WHERE national_id = %s', (user_cccd,))
        cccd = cur.fetchone()
        # If cccd exists show error and validation checks
        if cccd:
            msg = 'National ID already exists!'
            return render_template('register_acc.html', msg=msg)
        else:
            check2= True

        if check1==True and check2==True:
            cur.execute("INSERT INTO account(account_id, email, password, name, address, national_id, phone, date_of_birth) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)", (user_email, user_pw, user_name, user_address, user_cccd, user_phone, user_date))
            mydb.commit()
            # msg = 'You have successfully registered!'
            # cur.close()
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    
    return render_template('register_acc.html')


@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('account_id', None)
    session.pop('email_login', None)
    session.pop('pw', None)
    session.pop('name', None)
    session.pop('address', None)
    session.pop('national_id', None)
    session.pop('phone', None)
    session.pop('date_of_birth', None)
    session.pop('cash_amount', None)
    session.pop('data_stocks_asset', None)
    session.pop('data_history', None)
    session.pop('data_port', None)
    session.pop('data_stock', None)
    session.pop('search_stocks', None)
    session.pop('stocks_port', None)
    session.pop('market_port', None)
    session.pop('name_port', None) 
    session.pop('info_port', None)
    session.pop('price', None)
    session.pop('labels', None)
    session.pop('values', None)
    session.pop('stock_idd', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def home_iuh_invest():
    if 'loggedin' in session:
        session.pop('search_stocks', None)
        session.pop('stocks_port', None)
        session.pop('data_stock', None)
        session.pop('data_port',None)
        session.pop('price', None)
        cur = mydb.cursor()
        cur.execute('SELECT portfolio.portfolio_id, portfolio.portfolio, portfolio.type, portfolio.description, portfolio.created_date FROM portfolio LEFT JOIN account ON portfolio.account_id = account.account_id WHERE email = %s', (session['email_login'],))
        port_home = cur.fetchall()
        # print('ok4:', port_home)
        if port_home:
            return render_template('home_invest.html', data=port_home)
        else:
            return render_template('home_invest.html')

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/delete/<int:id>')
def delete_portfo(id):
    cur = mydb.cursor()
    cur.execute('SELECT * FROM portfolio')
    del_port = cur.fetchall()
    if del_port:
        cur.execute('DELETE FROM portfolio where portfolio_id = {0}'.format(id))
        mydb.commit()
    return redirect(url_for('home_iuh_invest'))


@app.route('/portfolio/<int:id_port>')
def show_portfo(id_port):
    # print(name)
    cur = mydb.cursor()

    market_port = sql_cursor.market_value_portfolio(cur, id_port)

    if market_port:
        session['name_port'] = market_port[0]
        session['market_port'] = market_port[1]
    else:
        cur.execute("SELECT portfolio\
                     FROM LOGIN.portfolio\
                     WHERE portfolio_id =%s\
                    ", (id_port,))
        name_port = cur.fetchone()
        session['name_port'] = name_port[0]
        session['market_port'] = 0
    
    info_port = sql_cursor.market_value_close_price(cur, id_port)

    if info_port:
        session['info_port'] = info_port
    else:
        session['info_port'] = ''

    #Chart
    lst_cha = []
    lst_con = []
    cur = mydb.cursor()
    cur.execute("SELECT * FROM transaction AS t WHERE portfolio_id = %s AND date_time <= %s", (id_port, '2023-01-11'))
    transaction = cur.fetchall()

    if transaction != []:
        df_trans = pd.DataFrame(transaction)
        df_trans.columns = ['transaction_id', 'trans_type', 'amount_trans', 'price', 'date_time', 'account_id', 'portfolio_id', 'stock_id']
        df_trans = df_trans.sort_values(by=['stock_id']).reset_index(drop=True)
        df_trans[['date', 'time']] = df_trans['date_time'].astype(str).str.split(" ", expand = True)
        check = df_trans['stock_id'][0]
        amount=0
        for index, row in df_trans.iterrows():
            if index ==0:
                amount = row['amount_trans']
                df_trans['amount_curr']= amount
                continue

            if row['stock_id'] != check:
                check = row['stock_id']
                amount = row['amount_trans']
                df_trans['amount_curr'][index]= amount
                continue

            if row['trans_type'] == 'BUY':
                amount += row['amount_trans']
                df_trans['amount_curr'][index]= amount
            else:
                amount -= row['amount_trans']
                df_trans['amount_curr'][index]= amount

        df_trans = df_trans.iloc[:,5:].groupby(['stock_id', 'date']).max('date').reset_index()
        df_trans['date'] = df_trans['date'].astype(str)

        cur = mydb.cursor()
        cur.execute("SELECT * FROM stock_trading")
        stock_trading = cur.fetchall()
        df_stock_trading = pd.DataFrame(stock_trading)
        df_stock_trading.columns = ['stock_trading_id', 'date', 'close_price', 'stock_id']
        df_stock_trading['date']= df_stock_trading['date'].astype(str)
        
        df_chart = pd.merge(df_stock_trading, df_trans, how="inner", on=['stock_id', 'date']).sort_values(by='date').reset_index()
        # print(df_chart)
        df_chart['market_value'] = df_chart['amount_curr'] * df_chart['close_price']
        print(df_chart)

        dict_ = {}
        dict_date = {}
        check_date = df_chart['date'][0]
        for index in df_chart.index:
            if df_chart['date'][index] == '2023-01-01':
                dict_[df_chart['stock_id'][index]] = df_chart['market_value'][index]
            else:
                if df_chart['date'][index] != check_date or index == len(df_chart.index)-1:
                    new_row = dict_.copy()
                    dict_date[check_date] = new_row
                    check_date = df_chart['date'][index]
                if df_chart['stock_id'][index] in dict_.keys():
                    dict_[df_chart['stock_id'][index]] = df_chart['market_value'][index]
                    new_row = dict_.copy()
                    if index == len(df_chart.index)-1:
                        dict_date[check_date] = new_row
       
        res = 0
        labels = []
        values = []
        for key in dict_date.keys():
            labels.append(key)
            for val in dict_date[key].values():
                res += val
            values.append(res)
     
        session['labels'] = labels
        session['values'] = values
    else:
        session.pop('labels', None)
        session.pop('values', None)

    return redirect(url_for('home_iuh_invest'))


@app.route('/profiles', methods=['GET', 'POST'])
def account():
    session.pop('search_stocks', None)
    session.pop('stocks_port', None)
    session.pop('data_stock', None)
    session.pop('data_port',None)
    session.pop('price', None)
    session.pop('labels', None)
    session.pop('values', None)
    return render_template('account.html')

@app.route('/asset', methods=['GET', 'POST'])
def asset():
    cur = mydb.cursor()

    history = sql_cursor.history_asset(cur, session['account_id'])
    
    if history:
        if history[0][0] != None:
            session['data_history'] = history
    
    stock_account_id = sql_cursor.asset_stock_account(cur, session['account_id'])
    
    if stock_account_id:
        if stock_account_id[0][0] != None:
            session['data_stocks_asset'] = stock_account_id

    session.pop('search_stocks', None)
    session.pop('stocks_port', None)
    session.pop('data_stock', None)
    session.pop('data_port',None)
    session.pop('price', None)
    session.pop('name_port', None)
    session.pop('market_port', None)
    session.pop('info_port', None)
    session.pop('labels', None)
    session.pop('values', None)
    return render_template('asset.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    session.pop('search_stocks', None)
    session.pop('stocks_port', None)
    session.pop('data_stock', None)
    session.pop('data_port',None)
    session.pop('price', None)
    session.pop('name_port', None)
    session.pop('market_port', None)
    session.pop('info_port', None)
    session.pop('labels', None)
    session.pop('values', None)
    cur = mydb.cursor()
    if request.method == "POST":
        cash_in = request.form.get("Cashin")
        cur.execute('SELECT * FROM account WHERE email = %s', (session['email_login'],))
        cash_in_sql = cur.fetchone()
        if cash_in_sql:
            cur.execute("UPDATE account SET cash_amount={0}+cash_amount".format(cash_in))
            mydb.commit()
            cur.execute('SELECT format(cash_amount,0) FROM account WHERE email = %s', (session['email_login'],))
            update_cash_amount = cur.fetchone()
            if update_cash_amount:
                session['cash_amount'] = update_cash_amount[0]
                # print('cash in: ',session['cash_amount'])
            flash('CASH IN SUCCESS!')
            return render_template('deposit.html')
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    session.pop('search_stocks', None)
    session.pop('stocks_port', None)
    session.pop('data_stock', None)
    session.pop('data_port',None)
    session.pop('price', None)
    session.pop('name_port', None)
    session.pop('market_port', None)
    session.pop('info_port', None)
    session.pop('labels', None)
    session.pop('values', None)
    cur = mydb.cursor()
    if request.method == "POST":
        cash_out = request.form.get("Cash_out")
        cur.execute('SELECT * FROM account WHERE email = %s', (session['email_login'],))
        cash_out_sql = cur.fetchone()
        if cash_out_sql:
            if float(cash_out) <= float(session['cash_amount'].replace(',','')):
                cur.execute("UPDATE account SET cash_amount= cash_amount-{0}".format(cash_out))
                mydb.commit()
                cur.execute('SELECT format(cash_amount,0) FROM account WHERE email = %s', (session['email_login'],))
                update_cash_amount = cur.fetchone()
                if update_cash_amount:
                    session['cash_amount'] = update_cash_amount[0]
                    # print('cashout: ',session['cash_amount'])
                flash('CASH OUT SUCCESS!')
                return render_template('withdraw.html')
            else:
                flash('CASH OUT FAIL!')
                return render_template('withdraw.html')
    return render_template('withdraw.html')

@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    session.pop('name_port', None)
    session.pop('market_port', None)
    session.pop('info_port', None)
    session.pop('labels', None)
    session.pop('values', None)
    cur = mydb.cursor()
    if request.method =='POST' and 'search_suggest' in request.form:
        # print('ok')
        stocks_port = request.form.get("search_suggest")
        session['stocks_port'] = stocks_port
        # cur.execute('SELECT portfolio_id FROM portfolio WHERE portfolio = %s AND account_id =%s', (session['stocks_port'], session['account_id']))
        # id_result = cur.fetchone()
        # session['id_port'] = id_result[0]
        # print(session['id_port'])
        data_trans_port = sql_cursor.market_value_row_by_row(cur, object=stocks_port)
        if data_trans_port != []:
            if data_trans_port[0][0] != None:
                session['data_port'] = data_trans_port 
                return render_template('stocks.html')
        else:
            check_port_exist = sql_cursor.check_portfolio_exist(cur, account=session['account_id'], portfolio=stocks_port)
            if check_port_exist:
                session['data_port'] = ''
                return render_template('stocks.html')
            else:
                flash("THERE'S NO " + stocks_port + " IN ACCOUNT")
                return render_template('stocks.html')
        
    if 'search_stocks' in request.form:
        if session.get('stocks_port') != None:
            search_stocks = request.form.get("search_stocks")
            session['search_stocks'] = search_stocks

            cur.execute("SELECT stock_id\
                                     FROM LOGIN.stock\
                                     WHERE stock=%s\
                                    ", (session['search_stocks'],))
            session['stock_idd'] = cur.fetchone()[0]

            cur.execute("SELECT stock FROM LOGIN.stock")
            code_stock_sql = cur.fetchall()
            code_stock = []
            for i in code_stock_sql:
                code_stock.append(i[0])
            if search_stocks in code_stock:
                session['price'] = sql_cursor.check_price_stock_maxdate(cur,session['search_stocks'])[0]
                
                data_history = sql_cursor.transaction_stock(cur, session['account_id'], search_stocks)
                if data_history:
                    session['data_stock'] = data_history
                    # return render_template('stocks.html')
                else:
                    session['data_stock'] = data_history
                    # return render_template('stocks.html')
            else:
                flash("THERE'S NO " + search_stocks + " IN PORTFOLIO") # there's no "AAA" in portfolio
                return render_template('stocks.html')
        else:
            flash("PLEASE ENTER PORTFOLIO NAME!")
            return render_template('stocks.html')

    if 'btnSubmit_buy' in request.form:
        if session.get('search_stocks') != None:
            
            # price=0
            if request.form.get("Amount_stocks") == '':
                flash("PLEASE ENTER NUMBER OF SHARES!")
                return render_template('stocks.html')
                
            amount_stocks = request.form.get("Amount_stocks")
            

            total_price_curr = session['price'] * int(amount_stocks) # tổng tiền hiện tại
            
            cur.execute('SELECT portfolio_id FROM portfolio WHERE portfolio = %s AND account_id =%s', (session['stocks_port'], session['account_id']))
            id_result = cur.fetchone()
            id_port = id_result[0]
            print(id_port)
            if id_result: # Nếu có portfolio lấy giá trị Mã portfolio
                id_port = id_result[0]
                # print(id_port)
                cur.execute("SELECT s.stock\
                             FROM LOGIN.port_stocks AS ps\
                             LEFT JOIN LOGIN.stock AS s on ps.stock_id = s.stock_id\
                             WHERE s.stock = %s AND ps.portfolio_id = %s", (session['search_stocks'], id_port,))
                check_port_stock = cur.fetchone()
                print(check_port_stock)
                if check_port_stock: # nếu check_port_stock có tồn tại trong database thì update lại giá trị
                    if total_price_curr <= float(session['cash_amount'].replace(',','')):
                        cur.execute("INSERT INTO transaction(transaction_id, portfolio_id, account_id, stock_id, trans_type, price_trans, amount_trans)\
                                     VALUES (NULL, %s, %s, %s, %s, %s, %s)", \
                                    (id_port, session['account_id'], session['stock_idd'], "BUY", session['price'], amount_stocks,))
                        cur.execute("UPDATE port_stocks SET amount_buy = amount_buy + %s WHERE stock_id = %s AND portfolio_id = %s", (int(amount_stocks), session['stock_idd'], id_port,))
                        cur.execute("UPDATE account SET cash_amount= cash_amount-{0}".format(total_price_curr))
                        mydb.commit()
                      
                        cur.execute('SELECT format(cash_amount,0) FROM account WHERE email = %s', (session['email_login'],))
                        update_cash_amount = cur.fetchone()
                        if update_cash_amount: # update lại giá trị tài sản trong session của flask
                            session['cash_amount'] = update_cash_amount[0]
                        session.pop('search_stocks', None)
                        session.pop('stocks_port', None)
                        session.pop('price', None)
                        flash('BUY COMPLETED')
                        return render_template('stocks.html')
                    else:
                        # session.pop('search_stocks', None)
                        flash("DON'T HAVE ENOUGH MONEY!")
                        return render_template('stocks.html')
                else: # nếu check_port_stock không tồn tại trong database thì thêm giá trị mới vào trong database
                    if total_price_curr <= float(session['cash_amount'].replace(',','')):
                        cur.execute("INSERT INTO transaction(transaction_id, portfolio_id, account_id, stock_id, trans_type, price_trans, amount_trans)\
                                     VALUES (NULL, %s, %s, %s, %s, %s, %s)",\
                                     (id_port, session['account_id'], session['stock_idd'], "BUY", session['price'], amount_stocks,))
                        cur.execute("INSERT INTO port_stocks(port_stocks_id, portfolio_id, stock_id, amount_buy) VALUES (NULL, %s, %s, %s)", (id_port, session['stock_idd'], int(amount_stocks),))
                        cur.execute("UPDATE account SET cash_amount= cash_amount-{0}".format(total_price_curr))
                        mydb.commit()
                        cur.execute('SELECT format(cash_amount,0) FROM account WHERE email = %s', (session['email_login'],))
                        update_cash_amount = cur.fetchone()
                        if update_cash_amount: # Cập nhật lại giá trị tài sản
                            session['cash_amount'] = update_cash_amount[0]
                        session.pop('search_stocks', None)
                        session.pop('stocks_port', None)
                        session.pop('price', None)
                        flash('BUY COMPLETED!')
                        return render_template('stocks.html')
                    else:
                        flash("INSUFFICIENT FUNDS!")
                        return render_template('stocks.html')
        else:
            flash("PLEASE ENTER STOCK SYMBOL!")
        return render_template('stocks.html')
    
    
    if 'btnSubmit_sell' in request.form :
        if session.get('search_stocks') != None:
            # price=0
            if request.form.get("Amount_stocks") == '':
                flash("PLEASE ENTER NUMBER OF SHARES!")
                return render_template('stocks.html')
            amount_stocks = request.form.get("Amount_stocks")
            # price = price_stock(session['search_stocks'])
            total_price_curr = session['price'] * int(amount_stocks)
            cur.execute('SELECT portfolio_id FROM portfolio WHERE portfolio = %s AND account_id =%s', (session['stocks_port'], session['account_id']))
            id_result = cur.fetchone()
            
            if id_result: # Nếu có portfolio lấy giá trị Mã portfolio
                id_port = id_result[0]
                        
                cur.execute("SELECT s.stock, ps.amount_buy\
                             FROM LOGIN.port_stocks AS ps\
                             LEFT JOIN LOGIN.stock AS s on ps.stock_id = s.stock_id\
                             WHERE s.stock = %s AND ps.portfolio_id = %s", (session['search_stocks'], id_port,))
    
                check_port_stock = cur.fetchone()
                # print(check_port_stock)
                if check_port_stock: # nếu check_port_stock có tồn tại trong database thì update lại giá trị
                    if int(amount_stocks) <= check_port_stock[1]: # số lượng cổ phiếu bán phải nhỏ hơn hoặc bằng số lượng cổ phiếu đang có
                        cur.execute("INSERT INTO transaction(transaction_id, portfolio_id, account_id, stock_id, trans_type, price_trans, amount_trans)\
                                     VALUES (NULL, %s, %s, %s, %s, %s, %s)", \
                                    (id_port, session['account_id'], session['stock_idd'], "BUY", session['price'], amount_stocks,))
                        #Nếu bán thì sẽ cập nhật lại giá hiện tại đang bán và số lượng hiện có trừ đi số lượng bán
                        cur.execute("UPDATE port_stocks SET amount_buy = amount_buy - %s WHERE stock_id = %s AND portfolio_id = %s", (int(amount_stocks), session['stock_idd'], id_port,))
                        cur.execute("UPDATE account SET cash_amount= cash_amount+{0}".format(total_price_curr))
                        mydb.commit()

                        # Cập nhật lại tổng giá tiền
                        cur.execute('SELECT format(cash_amount,0) FROM account WHERE email = %s', (session['email_login'],))
                        update_cash_amount = cur.fetchone()
                        if update_cash_amount: # update lại giá trị tài sản trong session của flask
                            session['cash_amount'] = update_cash_amount[0]
                        cur.execute("SELECT amount_buy FROM LOGIN.port_stocks WHERE stock_id = %s AND portfolio_id = %s", (session['stock_idd'], id_port,))
                        check_amount_buy = cur.fetchone()
                        if check_amount_buy[0] == 0: # Nếu amount_buy bằng 0 thì xoá đi khỏi database
                            cur.execute("DELETE FROM port_stocks WHERE amount_buy=%s AND stock_id = %s AND portfolio_id = %s",(0, session['stock_idd'], id_port,))
                            mydb.commit()   
                        session.pop('search_stocks', None)
                        session.pop('stocks_port', None)
                        session.pop('price', None)
                        flash('SELL COMPLETED!')
                        return render_template('stocks.html')
                    else:
                        flash("DON'T HAVE ENOUGH SHARES!")
                        return render_template('stocks.html')
                else: # nếu check_port_stock không tồn tại trong database thì thêm giá trị mới vào trong database
                    flash('DON"T HAVE STOCK IN PORTFOLIO!')
                    return render_template('stocks.html')
        else:
            flash("PLEASE ENTER STOCK SYMBOL!")
        return render_template('stocks.html')
    
    
    # flash("YOU HAVE NOT ENTERED STOCK!")
    return render_template('stocks.html')

@app.route('/portfolio', methods=['GET', 'POST'])
def home_portfolio():
    # Check if account exists using MySQL
    session.pop('search_stocks', None)
    session.pop('stocks_port', None)
    session.pop('data_stock', None)
    session.pop('data_port',None)
    session.pop('price', None)
    cur = mydb.cursor()
    if request.method == "POST" and 'Portfolio' in request.form and 'type' in request.form: 
        details = request.form
        user_portfolio = details['Portfolio']
        user_type_port = details['type']
        user_description = details['comment']
        cur.execute("INSERT INTO portfolio(portfolio_id, portfolio, type, description, account_id) VALUES (NULL, %s, %s, %s, %s)", (user_portfolio, user_type_port, user_description, session['account_id']))
        mydb.commit()
        flash('Create Portfolio Success!')
        # cur.close()
        return render_template('portfolio.html')
    return render_template('portfolio.html')

if __name__ == '__main__':
    app.run(host= '127.0.0.1', port=5000, debug=True)
