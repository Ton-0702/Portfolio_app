class sql_cursor:
    def check_login(cur, user_email, user_pw):
        cur.execute('SELECT account_id, email, password, name, address, national_id, phone, date_of_birth, format(cash_amount,0) \
                     FROM account\
                     WHERE email = %s AND password = %s', (user_email, user_pw,))
        return cur.fetchone()
    
    def market_value_portfolio(cur, portfolio):
        cur.execute("WITH stock_trading_maxdate AS(\
                    SELECT st.stock_id, st.trading_date, st.close_price\
                    FROM (\
                            SELECT st.stock_id, MAX(st.trading_date) AS MAX_DATE\
                            FROM LOGIN.stock_trading AS st\
                            GROUP BY st.stock_id\
                            ) A\
                    INNER JOIN LOGIN.stock_trading AS st ON A.stock_id = st.stock_id AND A.MAX_DATE = st.trading_date\
                )\
                \
                SELECT p.portfolio, ROUND(SUM(ps.amount_buy * stm.close_price),3)  AS market_value\
                FROM LOGIN.port_stocks AS ps\
                LEFT JOIN LOGIN.portfolio AS p ON ps.portfolio_id = p.portfolio_id\
                LEFT JOIN LOGIN.stock AS s ON ps.stock_id = s.stock_id\
                LEFT JOIN stock_trading_maxdate AS stm ON s.stock_id = stm.stock_id\
                WHERE ps.portfolio_id = %s\
                GROUP BY p.portfolio_id, p.portfolio\
                ", (portfolio,))
        return cur.fetchone()

    def market_value_close_price(cur, portfolio):
        cur.execute("WITH stock_trading_maxdate AS(\
                    SELECT st.stock_id, st.trading_date, st.close_price\
                    FROM (\
                            SELECT st.stock_id, MAX(st.trading_date) AS MAX_DATE\
                            FROM LOGIN.stock_trading AS st\
                            GROUP BY st.stock_id\
                            ) A\
                    INNER JOIN LOGIN.stock_trading AS st ON A.stock_id = st.stock_id AND A.MAX_DATE = st.trading_date\
                )\
                \
                SELECT s.stock, ps.amount_buy, stm.close_price, ROUND((ps.amount_buy * stm.close_price),3) AS market_value\
                FROM LOGIN.port_stocks AS ps\
                LEFT JOIN LOGIN.portfolio AS p ON ps.portfolio_id = p.portfolio_id\
                LEFT JOIN LOGIN.stock AS s ON ps.stock_id = s.stock_id\
                LEFT JOIN stock_trading_maxdate AS stm ON s.stock_id = stm.stock_id\
                WHERE ps.portfolio_id = %s\
                ", (portfolio,))
        return cur.fetchall()

    def market_value_row_by_row(cur, object):
        # cur = mydb.cursor()
        cur.execute("WITH stock_trading_maxdate AS(\
                        SELECT st.stock_id, st.trading_date, st.close_price\
                        FROM (\
                                SELECT st.stock_id, MAX(st.trading_date) AS MAX_DATE\
                                FROM LOGIN.stock_trading AS st\
                                GROUP BY st.stock_id\
                                ) A\
                        INNER JOIN LOGIN.stock_trading AS st ON A.stock_id = st.stock_id AND A.MAX_DATE = st.trading_date\
                    )\
                    \
                    SELECT s.stock, ps.amount_buy, ROUND((ps.amount_buy * stm.close_price),3) AS market_value\
                    FROM LOGIN.port_stocks AS ps\
                    LEFT JOIN LOGIN.portfolio AS p ON ps.portfolio_id = p.portfolio_id\
                    LEFT JOIN LOGIN.stock AS s ON ps.stock_id = s.stock_id\
                    LEFT JOIN stock_trading_maxdate AS stm ON s.stock_id = stm.stock_id\
                    WHERE p.portfolio = %s\
                    ", (object,))
        return cur.fetchall()
    
    def check_portfolio_exist(cur, account, portfolio):
        cur.execute("SELECT * \
                          FROM LOGIN.portfolio\
                          where account_id=%s and portfolio = %s\
                        ", (account, portfolio))
        return cur.fetchone()
    
    def history_asset(cur, account):
        cur.execute("SELECT s.stock, t.trans_type, t.amount_trans, t.price_trans, t.date_time\
                 FROM LOGIN.transaction AS t\
                 LEFT JOIN account AS a ON t.account_id = a.account_id\
                 LEFT JOIN stock AS s ON t.stock_id = s.stock_id\
                 WHERE a.account_id = %s \
                 ORDER BY t.date_time DESC", (account,))
        return cur.fetchall()
    
    def asset_stock_account(cur, account):
        cur.execute("\
                    WITH stock_trading_maxdate AS(\
                        SELECT st.stock_id, st.trading_date, st.close_price\
                        FROM (\
                                SELECT st.stock_id, MAX(st.trading_date) AS MAX_DATE\
                                FROM LOGIN.stock_trading AS st\
                                GROUP BY st.stock_id\
                                ) A\
                        INNER JOIN LOGIN.stock_trading AS st ON A.stock_id = st.stock_id AND A.MAX_DATE = st.trading_date\
                    )\
                    \
                    SELECT p.portfolio, s.stock, ps.amount_buy, stm.close_price, ROUND((ps.amount_buy * stm.close_price),3) AS market_value\
                    FROM LOGIN.port_stocks AS ps\
                    LEFT JOIN LOGIN.portfolio AS p ON ps.portfolio_id = p.portfolio_id\
                    LEFT JOIN LOGIN.stock AS s ON ps.stock_id = s.stock_id\
                    LEFT JOIN stock_trading_maxdate AS stm ON s.stock_id = stm.stock_id\
                    LEFT JOIN account AS a ON p.account_id = a.account_id\
                    WHERE a.account_id =  %s\
                ", (account,))
        return cur.fetchall()

    def check_price_stock_maxdate(cur, name_stock):
        cur.execute("\
                        SELECT st.close_price\
                        FROM (\
                                SELECT st.stock_id, MAX(st.trading_date) AS MAX_DATE\
                                FROM LOGIN.stock_trading AS st\
                                GROUP BY st.stock_id\
                            ) A\
                        INNER JOIN LOGIN.stock_trading AS st ON A.stock_id = st.stock_id AND A.MAX_DATE = st.trading_date\
                        INNER JOIN LOGIN.stock AS s ON st.stock_id = s.stock_id\
                        WHERE s.stock=%s\
                    ", (name_stock,))
        return cur.fetchone()

    def transaction_stock(cur, account, stock):
        cur.execute("SELECT s.stock, t.trans_type, t.amount_trans, t.price_trans, t.date_time\
                            FROM LOGIN.transaction AS t\
                            LEFT JOIN account AS a ON t.account_id = a.account_id\
                            LEFT JOIN stock AS s ON t.stock_id = s.stock_id\
                            WHERE a.account_id = %s AND s.stock=%s\
                            ORDER BY t.date_time DESC", (account, stock))
        return cur.fetchall()