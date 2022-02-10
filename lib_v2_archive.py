
import lib_v2_globals as g
from colorama import Fore, Back, Style

def process_sell_v1(**kwargs):
    SELL_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    # * reset to original limits
    g.long_buys = 0
    g.dstot_Dadj = 0
    g.since_short_buy = 0
    g.short_buys = 0
    # * all cover costs incl sell fee were calculated in buy
    if g.display:
        g.facecolor = "black"

    g.deltatime = (g.ohlc['Date'][-1] - g.session_first_buy_time).total_seconds() / 86400

    # * first get latest conversion price
    g.conversion = get_last_price(g.spot_src)

    g.cooldown = 0  # * reset cooldown
    g.buys_permitted = True  # * Allows buys again
    g.external_sell_signal = False  # * turn off external sell signal
    state_wr("last_buy_price", 1e+10)

    # * update buy counts
    g.tot_buys = g.tot_buys + g.curr_buys
    g.curr_buys = 0
    state_wr("tot_buys", g.tot_buys)

    # * reset ffmaps lo limit
    # * set new low threshholc
    g.ffmaps_lothresh = g.cvars['ffmaps_lothresh']
    state_wr("buyseries", [])

    # * calc new data.  g.subtot_qty is total holdings set in BUY routine
    g.subtot_value = g.subtot_qty * SELL_PRICE

    # * calc pct gain/loss relative to invesment, NOT capital
    g.last_pct_gain = ((g.subtot_value - g.subtot_cost) / g.subtot_cost) * 100

    g.curr_run_ct = 0  # + * clear current count

    # * recalc max_qty, comparing last to current, and saving max, then reset
    this_qty = state_r("max_qty")
    state_wr("max_qty", max(this_qty, g.subtot_qty))
    state_wr("curr_qty", 0)

    # * update buysell record
    tv = df['Timestamp'].iloc[-1]

    g.df_buysell['subtot'].iloc[0] = (g.subtot_cost)
    g.df_buysell['qty'].iloc[0] = g.subtot_qty
    g.df_buysell['pnl'].iloc[0] = g.pnl_running
    g.df_buysell['pct'].iloc[0] = g.pct_running
    g.df_buysell['sell'].iloc[0] = SELL_PRICE
    g.df_buysell['Timestamp'].iloc[0] = tv

    # * record last sell time as 'to' field
    state_wr("to", f"{tv}")

    # * turn off 'can sell' flag, as we have nothing more to see now
    state_wr("open_buyscansell", False)

    # * record total number of sell and latest sell price
    g.tot_sells = g.tot_sells + 1
    state_wr("tot_sells", g.tot_sells)
    state_wr("last_sell_price", SELL_PRICE)

    # * create SELL order
    order = {}
    order["type"] = "sellall"
    # = order["funds"] = False
    order["side"] = "sell"
    order["size"] = toPrec("amount",g.subtot_qty)
    order["price"] = toPrec("price",SELL_PRICE)
    # = order["stop_price"] = CLOSE * 1 / cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["pair"] = g.cvars["pair"]
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    order["uid"] = g.uid
    state_wr("order", order)

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    rs = binance_orders_v1(order)  # * SELL
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    # * order failed
    if not rs:
        return float("Nan")
    # * sell all (the default sell strategy) and clear the counters
    state_wr('open_buys', [])
    state_wr('qty_holding', [])

    # * cals final cost and sale of session
    purchase_price = g.subtot_cost
    sold_price = g.subtot_qty * SELL_PRICE

    _margin_int_pt = g.cvars[g.datatype]['margin_int_pt']
    g.margin_interest_cost = ((_margin_int_pt * g.deltatime) * g.subtot_cost)
    g.total_margin_interest_cost = g.total_margin_interest_cost + g.margin_interest_cost

    cmd = f"UPDATE orders set mxint = {g.margin_interest_cost}, mxinttot={g.total_margin_interest_cost} where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # * calc running total (incl fees)
    g.running_total = toPrec("price",get_running_bal(version=3, ret='one'))

    # * (INCL FEES)

    # - EXAMPLE... buy at 10, sell at 20, $1 fee
    # - (20-(10+1))/20
    # - (20-11)/20
    # - 9/20
    # - 0.45  = 45% = profit margin
    # - 20 * (1+.50) = 29 = new amt cap
    g.pct_return = (sold_price - (purchase_price + g.adjusted_covercost)) / sold_price  # ! x 100 for actual pct value
    if math.isnan(g.pct_return):
        g.pct_return = 0

    # * print to console
    g.running_buy_fee = toPrec("price",g.subtot_cost * g.cvars['buy_fee'])
    g.est_sell_fee = toPrec("price",g.subtot_cost * g.cvars['sell_fee'])
    sess_gross = toPrec("price",(SELL_PRICE - g.avg_price) * g.subtot_qty)


    sess_net = toPrec("price",sess_gross - (g.running_buy_fee + g.est_sell_fee))

    sess_net = toPrec("price",sess_gross - (g.running_buy_fee + g.est_sell_fee))
    total_fee = toPrec("price",g.running_buy_fee + g.est_sell_fee)
    g.adjusted_covercost = toPrec("price",(total_fee * (1 / g.subtot_qty)) + g.margin_interest_cost)
    g.coverprice = toPrec("price",g.adjusted_covercost + g.avg_price)

    g.total_reserve = toPrec("amount",(g.capital * g.this_close))
    g.pct_cap_return = toPrec("amount",(
                g.running_total / (g.total_reserve)))  # ! JWFIX (sess_net / (g.cvars['reserve_cap'] * SELL_PRICE))

    _reserve_seed = g.cvars[g.datatype]['reserve_seed']
    g.pct_capseed_return = toPrec("amount",(
                g.running_total / (_reserve_seed * g.this_close)))

    # * update DB with pct
    cmd = f"UPDATE orders set pct = {g.pct_return}, cap_pct = {g.pct_cap_return} where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # * DEBUG - print to console
    # g.running_buy_fee = g.subtot_cost * cvars.get('buy_fee')
    # g.est_sell_fee = g.subtot_cost * cvars.get('sell_fee')
    # sess_gross = (SELL_PRICE -g.avg_price) * g.subtot_qty
    # sess_net =  sess_gross - (g.running_buy_fee+g.est_sell_fee)
    # total_fee = g.running_buy_fee+g.est_sell_fee
    # g.covercost = total_fee * (1/g.subtot_qty)
    # g.coverprice = g.covercost + g.avg_price

    # print("..........................................")
    # print(f"running total buy fee: {g.running_buy_fee}")
    # print(f"total sell fee: {g.est_sell_fee}")
    # print(f"total fee: {total_fee}")
    # print(f"purch qty: {g.subtot_qty}")
    # print(f"current average: {g.avg_price}")
    # print(f"virt covercost: {g.covercost}")
    # print(f"coverprice: {g.coverprice}")
    # print(f"close: {SELL_PRICE}")
    # print(f"avg price: {g.avg_price}")
    # print(f"gross profit: {sess_gross}")
    # print(f"net profit: {sess_gross - total_fee}")
    # print("------------------------------------------")
    # waitfor()

    # g.dtime = (timedelta(seconds=int((get_now() - g.last_time) / 1000)))


    str = []
    str.append(f"[{g.gcounter:05d}]")

    now_hms = datetime.now()
    sts = f"{now_hms.hour:02}:{now_hms.minute:02}:{now_hms.second:02}"
    # str.append(f"[{order['order_time']}]")
    str.append(f"[{sts}]")

    _soldprice = toPrec("price",g.subtot_qty * SELL_PRICE)
    str.append(Fore.GREEN + f"Sold    " + f"{order['size']} @ ${SELL_PRICE} = ${_soldprice}")
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"Fee: " + Fore.CYAN + Style.BRIGHT + f"${g.est_sell_fee}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessGross: " + Fore.CYAN + Style.BRIGHT + f"${sess_gross}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessFee: " + Fore.CYAN + Style.BRIGHT + f"${total_fee}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessNet: " + Fore.CYAN + Style.BRIGHT + f"${sess_net}" + Style.RESET_ALL)
    str.append(Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)
    log2file(iline, "ansi.txt")

    g.cap_seed = toPrec("amount",g.cap_seed + (sess_net / g.this_close))
    _margin_x = g.cvars[g.datatype]['margin_x']
    g.capital = toPrec("amount",g.cap_seed * _margin_x)

    botstr = ""
    botstr += f"Sold {order['size']} @ ${SELL_PRICE} = ${_soldprice}"
    botstr += f"|CAP:{g.capital} ({truncate((g.cap_seed-1)*100,2)}%)"
    botstr += f"|T:${g.running_total}"

    botmsg(f"**{botstr}**")

    # with open(f"_profit_record_{g.session_name}.csv', 'a') as outfile:
    #     json.dump(g.state, outfile, indent=4)

    log2file(iline, "ansi.txt")

    # * reset average price
    g.avg_price = float("Nan")

    g.bsuid = g.bsuid + 1
    g.subtot_qty = 0
    # * set binlive to running total as default
    binlive = g.running_total
    # * save noew USDT balace to file
    if not g.cvars['offline']:
        balances = b.get_balance()
        binlive = balances[g.QUOTE]['total']
        cmd = f"UPDATE orders SET binlive = {binlive} where uid='{order['uid']}' and session = '{g.session_name}'"
        threadit(sqlex(cmd)).run()


    str = []
    str.append(f"{Back.YELLOW}{Fore.BLACK}")
    str.append(f"[{dfline['Date']}]")
    str.append(f"({g.session_name}/{g.dtime})")
    str.append(f"NEW CAP AMT: " + Fore.BLACK + Style.BRIGHT + f"{g.capital} ({g.cap_seed})" + Style.NORMAL)
    str.append(f"DB Total:" + Fore.BLACK + Style.BRIGHT + f" ${binlive}" + Style.NORMAL)
    #! JWFIX str.append(f"RT Total:" + Fore.BLACK + Style.BRIGHT + f" ${float(b.get_balance(field='close'))-int(read_val_from_file('/tmp/_starting_val'))}" + Style.NORMAL)

    str.append(f"{Back.RESET}{Fore.RESET}")
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)


    return SELL_PRICE

def process_buy_v2x(**kwargs):
    BUY_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']
    X = False

    buy_orderid = False
    sell_orderid = False
    g.stoplimit_price = BUY_PRICE * (1 - g.cvars['sell_fee'])

    # * 'convienience' vars,
    tv = df['Timestamp'].iloc[-1]  # * gets last timestamp

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    # + START v2 BUY
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡ NEW BUY ORDER

    # * save the current price to use for evaluating adjusted TRUE profit
    save_startprice(BUY_PRICE)

    #! try:
    # * create a BUY order
    order = build_order("buy", g.purch_qty, BUY_PRICE, 'limit', dfline)

    # * preserve last sell price (assumes only one sell order can exist)
    '''
    Anything in BTC balance is the result of SELL orders that used the WA values,
    so if a SELL order exists, its values represent all previous BUYS.
    If a SELL order does not exist, that means the order was filled, and the WA data are gone.
    For this reason, every order's [qty,price] is saved so we can reload the last order's data.
    '''

    # * A new BUY has been triggered, so first cancel all existing unfilled sells
    #= rs = g.ticker_src.fetch_open_orders(symbol=g.cvars['pair'])
    #= for oo in rs:
    #=     if oo['side'] == "sell":
    #=         canceled = g.ticker_src.cancel_order(oo['id'], g.cvars['pair'])
    #=         b.Iprint(f"CANCELLED SELL: {canceled['amount']} @ {canceled['price']} ({canceled['id']})")
    '''
    At this point - there are no SELL orders, possibly some unfilled BUY orders and a BTC balance
    from filled BUY orders
    '''
    # * execute buy order
    a_amount_quote = b.get_balance(base=g.QUOTE)  # bal = b.get_balance(base=g.BASE)['free']
    # =jprint(a_amount_quote)
    # * check balance to cover buy
    amount_quote = a_amount_quote['free']# bal = b.get_balance(base=g.BASE)['free']
    if order['size'] * order['price'] < amount_quote:
        # * submit order
        rs = binance_orders_v2(order)  # ! BUY
        if not rs:
            return float("Nan")  # * order failed -  return nothing and wait for next loop
        if rs['status'] != 0:
            # * some error happenned, so we just bounce
            jprint(rs)
            print("continuing...")
            return float("Nan")
        print(mkstr1("NEW BUY ENTERED:", rs, 'red'))
        buy_orderid = rs['return']['id']
        state_wr("last_buy_price", BUY_PRICE)
    else:
        b.Iprint("Insufficient Funds")
        return float("Nan")
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡ CALC NEW LIMIT SELL OREDR

    '''
    At this point...

    There are no SELL orders.
    Any BUY orders are orders NOT being held.
    Whatever is held is reflected in the BTC balance whose WA price/qty is recorded in the
    "last_price" and "last_amount" vars.  So, we need to create a SELL order that contains
    the current BTC balance amount with previous WA data and new BUY order WA data

    '''

    # # * get list of all holdings to sell
    #= oohold = []
    #= ooqty = []
    # # * last buy order
    #= oohold.append(rs['return']['price'])
    #= ooqty.append(rs['return']['amount'])
    # # * current SELL orders, if any
    #= try:
    #=     last_order = cload("/tmp/_last_sell")
    #=     if last_order:
    #=         ooqty.append(last_order[0])
    #=         oohold.append(last_order[1])
    #= except:
    #=     pass
    #=
    #= for i in range(len(oohold)):
    #=     print(f"\t[{i + 1}] {ooqty[i]} @ {oohold[i]}")

    # # * calc avg price using weighted averaging - price and qty are [list] sums
    g.subtot_cost, g.subtot_qty, g.avg_price, g.adj_subtot_cost, g.adj_avg_price = wavg(ooqty, oohold)
    print(f"\tqty: {g.subtot_qty} avg: {g.avg_price} cover: {g.adj_avg_price}")
    #= # exit()
    #=
    #= sell_at = g.avg_price * 1.002
    #= str = Fore.GREEN + f"NEW SELL VALUES: {toPrec('amount', g.subtot_qty)} @ ${sell_at} = ${toPrec('price', toPrec('amount', g.subtot_qty) * sell_at)} " + Style.RESET_ALL
    #= print(str, end="", flush=True)
    # # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    #
    # # * need to give time for binance records to be updated so we can see the last BUY
    #= # time.sleep(5)
    #
    # # * add last SELL was data, if it exists
    #= tbal = b.get_balance(base=g.BASE)['total']  # bal = b.get_balance(base=g.BASE)['free']
    #= # tbal = bal['total']['BTC']  # * use current balace of BTC, in case some SELL orders have been partially filled
    #
    #= if tbal > 0:
    #=     order = build_order("sell", float(tbal), sell_at, 'limit', dfline)
    #=     rs = binance_orders_v2(order)  # ! REBUILD SELL
    #=     sell_orderid = rs['return']['id']
    #=     str = Fore.GREEN + f" ... (id:{sell_orderid}) " + Style.RESET_ALL
    #=     print(str, flush=True)
    #=     b.Iprint(f"last_buy_price set to {state_r('last_buy_price')}")
    #= else:
    #=     state_wr("last_buy_price", 1e+10)
    #=     print(f"Nothing to sell - last_buy_price reset to {state_r('last_buy_price')}", flush=True)
    # #! except Exception as e:
    # #!     print(f"ERROR (tbal): {e}")
    # #!     pass
    #

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    # + END v2 BUY
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

    print("≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡")

    # ! trx OK, so continue as normal
    # * calc total cost this run
    qty_holding_list = state_r('qty_holding')
    open_buys_list = state_r('open_buys')

    # * calc current total cost of session
    sess_cost = 0
    for i in range(len(qty_holding_list)):
        sess_cost = sess_cost + (open_buys_list[i] * qty_holding_list[i])

    g.est_buy_fee = get_est_buy_fee(BUY_PRICE * g.purch_qty)
    g.running_buy_fee = toPrec("price", g.running_buy_fee + g.est_buy_fee)
    g.est_sell_fee = get_est_sell_fee(g.subtot_cost)

    # * this is the total fee in dollars amount
    total_fee = toPrec("price", g.running_buy_fee + g.est_sell_fee)
    g.adjusted_covercost = toPrec("price", total_fee * (1 / g.subtot_qty))
    g.coverprice = toPrec("price", g.adjusted_covercost + g.avg_price)

    if g.buymode == "S":
        state_ap("buyseries", 1)
        # * if we are in 'Dribble' mode, we want to increase buys, so we keep the dstot_lo mark loose
        g.dstot_Dadj = 0

    if g.buymode == "L":
        state_ap("buyseries", 0)
        g.long_buys += 1
        # * Once in "Long" mode, we increase the marker to reduce buys so as not to use up all our resource_cap on long valleys
        # * this is deon by rasing tehg percentage incrementer
        g.dstot_Dadj = g.cvars['dstot_Dadj'] * g.long_buys

    if X:
        # * print to console
        str = []
        str.append(f"[{g.gcounter:05d}]")
        str.append(f"[{order['order_time']}]")

        if g.cvars['convert_price']:
            ts = list(g.ohlc_conv[(g.ohlc_conv['Date'] == order['order_time'])]['Close'])[0]
        else:
            ts = order['order_time'][0]

        cmd = f"UPDATE orders set SL = '{g.buymode}' where uid = '{g.uid}' and session = '{g.session_name}'"
        threadit(sqlex(cmd)).run()

        order_cost = toPrec("cost", order['size'] * BUY_PRICE)

        # str.append(f"[{ts}]")
        # if g.cvars[g.datatype]['testpair'][0] == "BUY_perf":
        #     str.append(f"[R:{g.rootperf[g.bsig[:-1]]}]")
        # str.append(Fore.RED + f"Hold [{g.buymode}] " + Fore.CYAN + f"{order['size']} @ ${BUY_PRICE} = ${order_cost}" + Fore.RESET)
        # str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price:,.2f}" + Style.RESET_ALL)
        # str.append(Fore.GREEN + f"COV: " + Fore.CYAN + Style.BRIGHT + f"${g.coverprice:,.2f}" + Style.RESET_ALL)
        # str.append(Fore.RED + f"Fee: " + Fore.CYAN + f"${g.est_buy_fee}" + Fore.RESET)
        # str.append(Fore.RED + f"QTY: " + Fore.CYAN + f"{g.subtot_qty}" + Fore.RESET)
        # iline = str[0]
        # for s in str[1:]:
        #     iline = f"{iline} {s}"
        # print(iline)
        #

        # botstr = ""
        # botstr += f"R:{g.rootperf[g.bsig[:-1]]}" if g.cvars[g.datatype]['testpair'][0] == "BUY_perf" else ""
        # botstr += f"|H[{g.buymode}] {order['size']} @ ${BUY_PRICE} = ${order_cost}"
        # botstr += f"|Q:{g.subtot_qty}"
        #

        # botmsg(f"__{botstr}__")

        # log2file(iline, "ansi.txt")

        state_wr("open_buyscansell", True)

    return BUY_PRICE


# * [def perf2bin:1]
    # ! JWFIX need error loop here, or in v2.py
    # while not expass or retry < 10:
    #     try:
    #         g.ohlc = get_ohlc(t.since)
    #         retry = 10
    #         expass = True
    #     except Exception as e:
    #         handleEx(e,"in load_data (lib_v2_ohlc:46)")
    #         print(f"Exception error: [{e}]")
    #         print(f'Something went wrong. Error occured at {datetime.now()}. Retrying in 1 minute.')
    #         # reinstantiate connections in case of timeout
    #         time.sleep(60)
    #         del g.ticker_src
    #         del g.spot_src
    #
    #         g.ticker_src = ccxt.binance({
    #             'enableRateLimit': True,
    #             'timeout': 50000,
    #             'apiKey': g.keys['key'],
    #             'secret': g.keys['secret'],
    #         })
    #         g.ticker_src.set_sandbox_mode(g.keys['testnet'])
    #
    #         retry = retry + 1
    #         expass = False



# * [def process_buy_v1:1]
def process_buy_v1(**kwargs):
    ax = kwargs['ax']
    BUY_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    def tots(dfline):
        m = float("Nan")
        # * if there is a BUY and not a SELL, add the subtot as a neg value
        if not math.isnan(dfline['buy']) and math.isnan(dfline['sell']):
            m = dfline['buy'] * -1
            # * if there is a SELL and not a BUY, add the subtot as a pos value
        if not math.isnan(dfline['sell']) and math.isnan(dfline['buy']):
            m = dfline['sell']
        rs = m * dfline['qty']
        return (rs)

    if g.curr_run_ct == 0:
        g.session_first_buy_time = g.ohlc['Date'][-1]

    g.stoplimit_price = BUY_PRICE * (1 - g.cvars['sell_fee'])

    # * show on chart we have something to sell
    if g.display:
        g.facecolor = g.cvars['styles']['buyface']['color']
    # * first get latest conversion price
    g.conversion = get_last_price(g.spot_src, quiet=True)

    # * we are in, so reset the buy signal for next run
    g.external_buy_signal = False

    # * calc new subtot and avg
    # ! need to add current price and qty before doing the calc

    # * these list counts are how we track the total number of purchases since last sell
    state_ap('open_buys', BUY_PRICE)  # * adds to list of purchase prices since last sell
    state_ap('qty_holding', g.purch_qty)  # * adds to list of purchased quantities since last sell, respectfully

    # * calc avg price using weighted averaging, price and cost are [list] sums

    g.subtot_cost, g.subtot_qty, g.avg_price, g.adj_subtot_cost, g.adj_avg_price = wavg(state_r('qty_holding'),
                                                                                        state_r('open_buys'))

    state_wr("last_avg_price", g.avg_price)
    state_wr("last_adj_avg_price", g.avg_price)

    # * update the buysell records
    g.df_buysell['subtot'] = g.df_buysell.apply(lambda x: tots(x),
                                                axis=1)  # * calc which col we are looking at and apply accordingly

    # * 'convienience' vars,
    tv = df['Timestamp'].iloc[-1]  # * gets last timestamp

    # * insert latest data into df, and outside the routibe we shift busell down by 1, making room for next insert as loc 0
    g.df_buysell['buy'].iloc[0] = BUY_PRICE
    g.df_buysell['qty'].iloc[0] = g.purch_qty
    g.df_buysell['Timestamp'].iloc[0] = tv  # * add last timestamp tp buysell record

    # * increment run counter and make sure the historical max is recorded
    g.curr_run_ct = g.curr_run_ct + 1
    state_wr("curr_run_ct", g.curr_run_ct)

    # * track ongoing number of buys since last sell
    g.curr_buys = g.curr_buys + 1

    # * update buy count ans set permissions
    g.buys_permitted = False if g.curr_buys >= g.cvars['maxbuys'] else True

    # * save useful data in state file
    state_wr("last_buy_date", f"{tv}")
    state_wr("curr_qty", g.subtot_qty)

    if g.is_first_buy:
        state_wr("first_buy_price", BUY_PRICE)
        g.is_first_buy = False
    state_wr("last_buy_price", BUY_PRICE)

    # ! pre-calc coverprice for limit order to cover cost
    PRE_est_buy_fee = get_est_buy_fee(BUY_PRICE * g.subtot_qty)
    PRE_running_buy_fee = g.running_buy_fee + PRE_est_buy_fee
    PRE_est_sell_fee = get_est_sell_fee(g.subtot_cost)
    PRE_total_fee = PRE_running_buy_fee + PRE_est_sell_fee
    PRE_adjusted_covercost = PRE_total_fee * (1 / g.subtot_qty)
    PRE_coverprice = PRE_adjusted_covercost + g.avg_price
    # ! --------------------------------------------------
    # * create a BUY order
    order = {}
    order["pair"] = g.cvars["pair"]
    # = order["funds"] = False
    order["side"] = "buy"
    # order["size"] = truncate(g.purch_qty, 5)  # ! JWFIX use 'precision' function


    order["size"] = toPrec("amount",g.purch_qty)
    # order["price"] = BUY_PRICE
    order["price"] = toPrec("price",BUY_PRICE)
    order["type"] = "market"
    order["limit_price"] = toPrec("price",PRE_coverprice)
    # = order["stop_price"] = CLOSE * 1/cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["uid"] = g.uid
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    state_wr("order", order)

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    rs = binance_orders_v1(order)  # * BUY
    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    if not rs:
        # * order failed -  return nothing and wait for next loop
        return float("Nan")

    # ! trx OK, so continue as normal
    # * calc total cost this run
    qty_holding_list = state_r('qty_holding')
    open_buys_list = state_r('open_buys')

    # * calc current total cost of session
    sess_cost = 0
    for i in range(len(qty_holding_list)):
        sess_cost = sess_cost + (open_buys_list[i] * qty_holding_list[i])

    g.est_buy_fee = get_est_buy_fee(BUY_PRICE *  g.purch_qty)
    g.running_buy_fee = toPrec("price",g.running_buy_fee + g.est_buy_fee)
    g.est_sell_fee = get_est_sell_fee(g.subtot_cost)

    # * this is the total fee in dollars amount
    total_fee = toPrec("price",g.running_buy_fee + g.est_sell_fee)
    # * to calculate the closing price necessary to cover this cost
    # * we have to calculate the $ value as a % of the unit cost.
    # * example...
    # * if fee is 10%, and price is $100, and we purchased 0.5,
    # * than the cover cost is (100*0.5)*0.10=5. to make that 5 we
    # * we need to sell at 110, as we only have 0.5 shares.  So the
    # * we need need to calc the minimum closing price as
    # * 5 * (1/qty), whish gives us
    # * 5 * (1/qty) = 5*(1/.5)=5*2=10 plus the original cost
    # * 100 = 110
    g.adjusted_covercost = toPrec("price",total_fee * (1 / g.subtot_qty))
    g.coverprice = toPrec("price",g.adjusted_covercost + g.avg_price)
    # ! -------------------------------------------------

    # print("..........................................")
    # print(f"running total buy fee: {g.running_buy_fee}")
    # print(f"est buy fee: {g.est_buy_fee}")
    # print(f"total sell fee: {g.est_sell_fee}")
    # print(f"total fee: {total_fee}")
    # print(f"purch qty: {g.subtot_qty}")
    # print(f"cost of purchase: {g.subtot_cost}")
    # print(f"current average: {g.avg_price}")
    # print(f"virt covercost: {g.adjusted_covercost} - {total_fee} * (1/{g.subtot_qty}),{total_fee} * ({1/g.subtot_qty})    ")
    # print(f"coverprice: {g.coverprice}")
    # print(f"close: {BUY_PRICE}")
    # print(f"avg price: {g.avg_price}")
    # print("------------------------------------------")
    # waitfor()

    if g.buymode == "S":
        state_ap("buyseries", 1)
        # * if we are in 'Dribble' mode, we want to increase buys, so we keep the dstot_lo mark loose
        g.dstot_Dadj = 0

    if g.buymode == "L":
        state_ap("buyseries", 0)
        g.long_buys += 1
        # * Once in "Long" mode, we increase the marker to reduce buys so as not to use up all our resource_cap on long valleys
        # * this is deon by rasing tehg percentage incrementer
        g.dstot_Dadj = g.cvars['dstot_Dadj'] * g.long_buys

    # * print to console
    str = []
    str.append(f"[{g.gcounter:05d}]")
    # str.append(f"[{order['order_time']}]")

    if g.cvars['convert_price']:
        ts = list(g.ohlc_conv[(g.ohlc_conv['Date'] == order['order_time'])]['Close'])[0]
    else:
        ts = order['order_time'][0]

    cmd = f"UPDATE orders set SL = '{g.buymode}' where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    order_cost = toPrec("cost",order['size'] * BUY_PRICE)
    now_hms = datetime.now()
    sts = f"{now_hms.hour:02}:{now_hms.minute:02}:{now_hms.second:02}"
    str.append(f"[{sts}]")
    if g.cvars[g.datatype]['testpair'][0] == "BUY_perf":
        str.append(f"[R:{g.rootperf[g.bsig[:-1]]}]")
    str.append(Fore.RED + f"Hold [{g.buymode}] " + Fore.CYAN + f"{order['size']} @ ${BUY_PRICE} = ${order_cost}" + Fore.RESET)
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"${g.avg_price:8.2f}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"COV: " + Fore.CYAN + Style.BRIGHT + f"${g.coverprice:8.2f}" + Style.RESET_ALL)
    str.append(Fore.RED + f"Fee: " + Fore.CYAN + f"${g.est_buy_fee}" + Fore.RESET)
    str.append(Fore.RED + f"QTY: " + Fore.CYAN + f"{g.subtot_qty}" + Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)


    botstr = ""
    botstr += f"R:{g.rootperf[g.bsig[:-1]]}" if g.cvars[g.datatype]['testpair'][0] == "BUY_perf" else ""
    botstr += f"|H[{g.buymode}] {order['size']} @ ${BUY_PRICE} = ${order_cost}"
    botstr += f"|Q:{g.subtot_qty}"


    botmsg(f"__{botstr}__")

    log2file(iline, "ansi.txt")

    state_wr("open_buyscansell", True)

    return BUY_PRICE

    # ! [process_buy_v2:1]
    # print("..........................................")
    # print(f"running total buy fee: {g.running_buy_fee}")
    # print(f"est buy fee: {g.est_buy_fee}")
    # print(f"total sell fee: {g.est_sell_fee}")
    # print(f"total fee: {total_fee}")
    # print(f"purch qty: {g.subtot_qty}")
    # print(f"cost of purchase: {g.subtot_cost}")
    # print(f"current average: {g.avg_price}")
    # print(f"virt covercost: {g.adjusted_covercost} - {total_fee} * (1/{g.subtot_qty}),{total_fee} * ({1/g.subtot_qty})    ")
    # print(f"coverprice: {g.coverprice}")
    # print(f"close: {BUY_PRICE}")
    # print(f"avg price: {g.avg_price}")
    # print("------------------------------------------")
    # waitfor()


    # ! [process_sell_v2:1]
    # * DEBUG - print to console
    # g.running_buy_fee = g.subtot_cost * cvars.get('buy_fee')
    # g.est_sell_fee = g.subtot_cost * cvars.get('sell_fee')
    # sess_gross = (SELL_PRICE -g.avg_price) * g.subtot_qty
    # sess_net =  sess_gross - (g.running_buy_fee+g.est_sell_fee)
    # total_fee = g.running_buy_fee+g.est_sell_fee
    # g.covercost = total_fee * (1/g.subtot_qty)
    # g.coverprice = g.covercost + g.avg_price

    # print("..........................................")
    # print(f"running total buy fee: {g.running_buy_fee}")
    # print(f"total sell fee: {g.est_sell_fee}")
    # print(f"total fee: {total_fee}")
    # print(f"purch qty: {g.subtot_qty}")
    # print(f"current average: {g.avg_price}")
    # print(f"virt covercost: {g.covercost}")
    # print(f"coverprice: {g.coverprice}")
    # print(f"close: {SELL_PRICE}")
    # print(f"avg price: {g.avg_price}")
    # print(f"gross profit: {sess_gross}")
    # print(f"net profit: {sess_gross - total_fee}")
    # print("------------------------------------------")
    # waitfor()
