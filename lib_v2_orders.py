import importlib
import json
import math
import os
import uuid
from datetime import datetime
import pandas as pd
from colorama import Fore, Back, Style  # ! https://pypi.org/project/colorama/
import lib_v2_binance as b
import lib_v2_globals as g
import lib_v2_tests_class

def binance_orders_v1(order):
    success = False
    resp = {'status': -1}

    # * submit order to remote proc, wait for replays

    if g.cvars['offline']:
        if g.cvars['testnet']:
            g.buy_fee = 0
            g.sell_fee = 0

        order['fees'] = 0
        if order['side'] == "buy":
            _fee = (order['size'] * order['price']) * g.buy_fee  # * sumulate fee
            order['fees'] = toPrec("price", _fee)

        if order['side'] == "sell":
            _fee = (order['size'] * order['price']) * g.sell_fee  # * sumulate fee
            order['fees'] = toPrec("price", _fee)

        order['session'] = g.session_name
        order['state'] = True
        order['record_time'] = get_datetime_str()
        success = True
    else:  # ! is live
        # * This is what a market order looks like:
        # = {'order_time': '2021-01-01 02:10:00',
        # =  'type': 'market',
        # =  'pair': 'BTC/USDT',
        # =  'price': 29248.69,
        # =  'limit_price': 29258.69,
        # =  'side': 'buy',
        # =  'size': 0.414,
        # =  'state': 'submitted',
        # =  'uid': '866f90f5c8134cf19b3da8481011c4e4'}


        trxlog(order,resp,1)

        if order['type'] == "market" or order['type'] == "sellall":
            resp = b.market_order(
                symbol=g.cvars['pair'],
                type="market",
                side=order['side'],
                amount=order['size']
            )

        trxlog(order,resp,2)

        # print(json.dumps(resp, indent=4))
        # * This is what a market sell order response looks like_
        # +  {
        # +      "return": {
        # +          "info": {
        # +              "symbol": "BTCUSDT",
        # +              "orderId": "8235272",
        # +             "orderListId": "-1",
        # +             "clientOrderId": "x-R4BD3S82d2afacfaf78ec4f62dbf8f",
        # +             "transactTime": "1642700720644",
        # +             "price": "0.00000000",
        # +             "origQty": "0.00041400",
        # +             "executedQty": "0.00041400",
        # +             "cummulativeQuoteQty": "17.84513466",
        # +             "status": "FILLED",
        # +             "timeInForce": "GTC",
        # +             "type": "MARKET",
        # +             "side": "SELL",
        # +             "fills": [
        # +                 {
        # +                     "price": "43104.19000000",
        # +                     "qty": "0.00041400",
        # +                     "commission": "0.00000000",
        # +                     "commissionAsset": "USDT",
        # +                     "tradeId": "1718715"
        # +                 }
        # +             ]
        # +         },
        # +         "id": "8235272",
        # +         "clientOrderId": "x-R4BD3S82d2afacfaf78ec4f62dbf8f",
        # +         "timestamp": 1642700720644,
        # +         "datetime": "2022-01-20T17:45:20.644Z",
        # +         "lastTradeTimestamp": null,
        # +         "symbol": "BTC/USDT",
        # +         "type": "market",
        # +         "timeInForce": "GTC",
        # +         "postOnly": false,
        # +         "side": "sell",
        # +         "price": 43104.19,
        # +         "stopPrice": null,
        # +         "amount": 0.000414,
        # +         "cost": 17.84513466,
        # +         "average": 43104.19,
        # +         "filled": 0.000414,
        # +         "remaining": 0.0,
        # +         "status": "closed",
        # +         "fee": {
        # +             "cost": 0.0,
        # +             "currency": "USDT"
        # +         },
        # +         "trades": [
        # +             {
        # +                 "info": {
        # +                     "price": "43104.19000000",
        # +                     "qty": "0.00041400",
        # +                     "commission": "0.00000000",
        # +                     "commissionAsset": "USDT",
        # +                     "tradeId": "1718715"
        # +                 },
        # +                 "timestamp": null,
        # +                 "datetime": null,
        # +                 "symbol": "BTC/USDT",
        # +                 "id": "1718715",
        # +                 "order": "8235272",
        # +                 "type": "market",
        # +                 "side": "sell",
        # +                 "takerOrMaker": null,
        # +                 "price": 43104.19,
        # +                 "amount": 0.000414,
        # +                 "cost": 17.84513466,
        # +                 "fee": {
        # +                     "cost": 0.0,
        # +                     "currency": "USDT"
        # +                 }
        # +             }
        # +         ],
        # +         "fees": [
        # +             {
        # +                 "cost": 0.0,
        # +                 "currency": "USDT"
        # +             }
        # +         ]
        # +     },
        # +     "status": 0
        # + }

        # * This is what a market buy order response looks like_
        # =  {
        # =      "return": {
        # =          "info": {
        # =              "symbol": "BTCUSDT",
        # =              "orderId": "8233908",
        # =              "orderListId": "-1",
        # =              "clientOrderId": "x-R4BD3S8236eabc1108f9468ad15c48",
        # =              "transactTime": "1642700521138",
        # =              "price": "0.00000000",
        # =              "origQty": "0.00041400",
        # =              "executedQty": "0.00041400",
        # =              "cummulativeQuoteQty": "17.84234844",
        # =              "status": "FILLED",
        # =              "timeInForce": "GTC",
        # =              "type": "MARKET",
        # =              "side": "BUY",
        # =              "fills": [
        # =                  {
        # =                      "price": "43097.46000000",
        # =                      "qty": "0.00041400",
        # =                      "commission": "0.00000000",
        # =                      "commissionAsset": "BTC",
        # =                      "tradeId": "1718467"
        # =                  }
        # =              ]
        # =          },
        # =          "id": "8233908",
        # =          "clientOrderId": "x-R4BD3S8236eabc1108f9468ad15c48",
        # =          "timestamp": 1642700521138,
        # =          "datetime": "2022-01-20T17:42:01.138Z",
        # =          "lastTradeTimestamp": null,
        # =          "symbol": "BTC/USDT",
        # =          "type": "market",
        # =          "timeInForce": "GTC",
        # =          "postOnly": false,
        # =          "side": "buy",
        # =          "price": 43097.46,
        # =          "stopPrice": null,
        # =          "amount": 0.000414,
        # =          "cost": 17.84234844,
        # =          "average": 43097.46,
        # =          "filled": 0.000414,
        # =          "remaining": 0.0,
        # =          "status": "closed",
        # =          "fee": {
        # =              "cost": 0.0,
        # =              "currency": "BTC"
        # =          },
        # =          "trades": [
        # =              {
        # =                  "info": {
        # =                      "price": "43097.46000000",
        # =                      "qty": "0.00041400",
        # =                      "commission": "0.00000000",
        # =                      "commissionAsset": "BTC",
        # =                      "tradeId": "1718467"
        # =                  },
        # =                  "timestamp": null,
        # =                  "datetime": null,
        # =                  "symbol": "BTC/USDT",
        # =                  "id": "1718467",
        # =                  "order": "8233908",
        # =                  "type": "market",
        # =                  "side": "buy",
        # =                  "takerOrMaker": null,
        # =                  "price": 43097.46,
        # =                  "amount": 0.000414,
        # =                  "cost": 17.84234844,
        # =                  "fee": {
        # =                      "cost": 0.0,
        # =                      "currency": "BTC"
        # =                  }
        # =              }
        # =          ],
        # =          "fees": [
        # =              {
        # =                  "cost": 0.0,
        # =                  "currency": "BTC"
        # =              }
        # =          ]
        # =      },
        # =      "status": 0
        # =  }

        if order['type'] == "limit":
            resp = b.limit_order(symbol=g.cvars['pair'], type="limit", side=order['side'], amount=order['size'],
                                 price=order['limit_price'])

        if resp['status'] != 0:
            b.Eprint("ERROR (see 'logs/trx.log') CONTINUING (until next sell: ", end="")
            if resp['return'] == "binance Account has insufficient balance for requested action.":
                b.Eprint(f"Insufficient balance: CURRENT {g.BASE} BALANCE: [{b.get_balance(base=g.BASE)['free']}]")
                log2file(f"CURRENT {g.QUOTE} BALANCE: [{b.get_balance(base=g.QUOTE)['free']}]", "trx.log")
                log2file(f"{order['size']} * {order['price']} = {order['size'] * order['price']}", "trx.log")

            log2file(json.dumps(resp, indent=4), "trx.log")
            log2file(json.dumps(order, indent=4), "trx.log")
        else:

            order['fees'] = resp['return']['fee']['cost']
            order['session'] = g.session_name
            order['state'] = resp['return']['status']
            order[
                'record_time'] = get_datetime_str()  # ! JWFIX  use fix_timestr_for_mysql() /// resp['return']['datetime']
            success = True

    update_db(order, g.quote_price)
    return success

def binance_orders_v2(order):
    resp =  {'status': -1}

    # * submit order to remote proc, wait for replays

    if g.cvars['offline']:
        if g.cvars['testnet']:
            g.buy_fee = 0
            g.sell_fee = 0

        order['fees'] = 0
        if order['side'] == "buy":
            _fee = (order['size'] * order['price']) * g.buy_fee  # * sumulate fee
            order['fees'] = toPrec("price", _fee)

        if order['side'] == "sell":
            _fee = (order['size'] * order['price']) * g.sell_fee  # * sumulate fee
            order['fees'] = toPrec("price", _fee)

        order['session'] = g.session_name
        order['state'] = True
        order['record_time'] = get_datetime_str()
    else:  # ! is live
        # * This is what a market order looks like:
        # = {'order_time': '2021-01-01 02:10:00',
        # =  'type': 'market',
        # =  'pair': 'BTC/USDT',
        # =  'price': 29248.69,
        # =  'limit_price': 29258.69,
        # =  'side': 'buy',
        # =  'size': 0.414,
        # =  'state': 'submitted',
        # =  'uid': '866f90f5c8134cf19b3da8481011c4e4'}

        # trxlog(order,resp,1)

        if order['type'] == "market" or order['type'] == "sellall":
            resp = b.market_order(
                symbol=g.cvars['pair'],
                type="market",
                side=order['side'],
                amount=order['size']
            )

        # trxlog(order,resp,2)

        # * This is what a market sell order response looks like_
        # +  {
        # +      "return": {
        # +          "info": {
        # +              "symbol": "BTCUSDT",
        # +              "orderId": "8235272",
        # +             "orderListId": "-1",
        # +             "clientOrderId": "x-R4BD3S82d2afacfaf78ec4f62dbf8f",
        # +             "transactTime": "1642700720644",
        # +             "price": "0.00000000",
        # +             "origQty": "0.00041400",
        # +             "executedQty": "0.00041400",
        # +             "cummulativeQuoteQty": "17.84513466",
        # +             "status": "FILLED",
        # +             "timeInForce": "GTC",
        # +             "type": "MARKET",
        # +             "side": "SELL",
        # +             "fills": [
        # +                 {
        # +                     "price": "43104.19000000",
        # +                     "qty": "0.00041400",
        # +                     "commission": "0.00000000",
        # +                     "commissionAsset": "USDT",
        # +                     "tradeId": "1718715"
        # +                 }
        # +             ]
        # +         },
        # +         "id": "8235272",
        # +         "clientOrderId": "x-R4BD3S82d2afacfaf78ec4f62dbf8f",
        # +         "timestamp": 1642700720644,
        # +         "datetime": "2022-01-20T17:45:20.644Z",
        # +         "lastTradeTimestamp": null,
        # +         "symbol": "BTC/USDT",
        # +         "type": "market",
        # +         "timeInForce": "GTC",
        # +         "postOnly": false,
        # +         "side": "sell",
        # +         "price": 43104.19,
        # +         "stopPrice": null,
        # +         "amount": 0.000414,
        # +         "cost": 17.84513466,
        # +         "average": 43104.19,
        # +         "filled": 0.000414,
        # +         "remaining": 0.0,
        # +         "status": "closed",
        # +         "fee": {
        # +             "cost": 0.0,
        # +             "currency": "USDT"
        # +         },
        # +         "trades": [
        # +             {
        # +                 "info": {
        # +                     "price": "43104.19000000",
        # +                     "qty": "0.00041400",
        # +                     "commission": "0.00000000",
        # +                     "commissionAsset": "USDT",
        # +                     "tradeId": "1718715"
        # +                 },
        # +                 "timestamp": null,
        # +                 "datetime": null,
        # +                 "symbol": "BTC/USDT",
        # +                 "id": "1718715",
        # +                 "order": "8235272",
        # +                 "type": "market",
        # +                 "side": "sell",
        # +                 "takerOrMaker": null,
        # +                 "price": 43104.19,
        # +                 "amount": 0.000414,
        # +                 "cost": 17.84513466,
        # +                 "fee": {
        # +                     "cost": 0.0,
        # +                     "currency": "USDT"
        # +                 }
        # +             }
        # +         ],
        # +         "fees": [
        # +             {
        # +                 "cost": 0.0,
        # +                 "currency": "USDT"
        # +             }
        # +         ]
        # +     },
        # +     "status": 0
        # + }

        # * This is what a market buy order response looks like_
        # =  {
        # =      "return": {
        # =          "info": {
        # =              "symbol": "BTCUSDT",
        # =              "orderId": "8233908",
        # =              "orderListId": "-1",
        # =              "clientOrderId": "x-R4BD3S8236eabc1108f9468ad15c48",
        # =              "transactTime": "1642700521138",
        # =              "price": "0.00000000",
        # =              "origQty": "0.00041400",
        # =              "executedQty": "0.00041400",
        # =              "cummulativeQuoteQty": "17.84234844",
        # =              "status": "FILLED",
        # =              "timeInForce": "GTC",
        # =              "type": "MARKET",
        # =              "side": "BUY",
        # =              "fills": [
        # =                  {
        # =                      "price": "43097.46000000",
        # =                      "qty": "0.00041400",
        # =                      "commission": "0.00000000",
        # =                      "commissionAsset": "BTC",
        # =                      "tradeId": "1718467"
        # =                  }
        # =              ]
        # =          },
        # =          "id": "8233908",
        # =          "clientOrderId": "x-R4BD3S8236eabc1108f9468ad15c48",
        # =          "timestamp": 1642700521138,
        # =          "datetime": "2022-01-20T17:42:01.138Z",
        # =          "lastTradeTimestamp": null,
        # =          "symbol": "BTC/USDT",
        # =          "type": "market",
        # =          "timeInForce": "GTC",
        # =          "postOnly": false,
        # =          "side": "buy",
        # =          "price": 43097.46,
        # =          "stopPrice": null,
        # =          "amount": 0.000414,
        # =          "cost": 17.84234844,
        # =          "average": 43097.46,
        # =          "filled": 0.000414,
        # =          "remaining": 0.0,
        # =          "status": "closed",
        # =          "fee": {
        # =              "cost": 0.0,
        # =              "currency": "BTC"
        # =          },
        # =          "trades": [
        # =              {
        # =                  "info": {
        # =                      "price": "43097.46000000",
        # =                      "qty": "0.00041400",
        # =                      "commission": "0.00000000",
        # =                      "commissionAsset": "BTC",
        # =                      "tradeId": "1718467"
        # =                  },
        # =                  "timestamp": null,
        # =                  "datetime": null,
        # =                  "symbol": "BTC/USDT",
        # =                  "id": "1718467",
        # =                  "order": "8233908",
        # =                  "type": "market",
        # =                  "side": "buy",
        # =                  "takerOrMaker": null,
        # =                  "price": 43097.46,
        # =                  "amount": 0.000414,
        # =                  "cost": 17.84234844,
        # =                  "fee": {
        # =                      "cost": 0.0,
        # =                      "currency": "BTC"
        # =                  }
        # =              }
        # =          ],
        # =          "fees": [
        # =              {
        # =                  "cost": 0.0,
        # =                  "currency": "BTC"
        # =              }
        # =          ]
        # =      },
        # =      "status": 0
        # =  }

        if order['type'] == "limit":
            otype = "STOP_LOSS" if order['side'] == "buy" else "TAKE_PROFIT"
            resp = b.limit_order(
                symbol=g.cvars['pair'],
                # type="limit",
                # type=otype,
                side=order['side'],
                amount=order['size'],
                price=order['price'],
                # stopPrice=order['limit_price']
                # stopPrice=order['stop_price']
            )

        if resp['status'] != 0:
            # * something went wrong
            jprint(order)
            jprint(resp)
            if resp['return'] == "binance Account has insufficient balance for requested action.":
                b.Eprint(f"Insufficient balance: CURRENT {g.BASE} BALANCE: [{b.get_balance(base=g.BASE)['free']}]")
                log2file(f"CURRENT {g.QUOTE} BALANCE: [{b.get_balance(base=g.QUOTE)['free']}]", "trx.log")
                log2file(f"{order['size']} * {order['price']} = {order['size'] * order['price']}", "trx.log")

            log2file(json.dumps(resp, indent=4), "trx.log")
            log2file(json.dumps(order, indent=4), "trx.log")
            return resp

        else:
            # * proceed as normal
            # * a BUY fee is returned as an scaler but
            # * a SELL fee is return as a list !?!?- JWFIX
            resp['return']['fee'] = 0 if not resp['return']['fee'] else resp['return']['fee']
            order['fees'] = resp['return']['fee']
            if isinstance(order['fees'],dict):
                order['fees'] = resp['return']['fee']['cost']
            order['session'] = g.session_name
            order['state'] = resp['return']['status']
            order['record_time'] = get_datetime_str()  # ! JWFIX  use fix_timestr_for_mysql() /// resp['return']['datetime']

    update_db(order, g.quote_price)
    return resp

def build_order(side,qty,price,otype,dfline):
    order = {}
    order["pair"] = g.cvars["pair"]
    order["side"] = side
    order["size"] = toPrec("amount", qty)  # order["price"] = BUY_PRICE
    order["price"] = toPrec("price", price)
    order["type"] = otype  # order["type"] = "market"
    order["uid"] = g.uid
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"

    with open(f'{g.tmpdir}/_last_{side}', 'w') as outfile:
        json.dump([qty,price],outfile)

    return order

def process_buy_v2(**kwargs):
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

    if g.subtot_qty == 0:
        print(f"ERROR: 'g.subtot_qty = 0")
        print(f"INPUTS:")
        print(f"qty_holding:")
        jprint(state_r('qty_holding'))
        print(f"open_buys:")
        jprint(state_r('open_buys'))

        print(f"OUTPUTS:")
        print(f"g.subtot_cost:     {g.subtot_cost}")
        print(f"g.subtot_qty:      {g.subtot_qty}")
        print(f"g.avg_price:       {g.avg_price}")
        print(f"g.adj_subtot_cost: {g.adj_subtot_cost}")
        print(f"g.adj_avg_price:   {g.adj_avg_price}")
        exit()

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
    g.buys_permitted = False if g.curr_buys >= g.maxbuys else True

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
    order["size"] = toPrec("amount",g.purch_qty)
    order["price"] = toPrec("price",BUY_PRICE)
    order["type"] = "limit"
    order["limit_price"] = toPrec("price",PRE_coverprice)
    # = order["stop_price"] = CLOSE * 1/cvars.get('closeXn')
    # = order["upper_stop_price"] = CLOSE * 1
    order["uid"] = g.uid
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    state_wr("order", order)

    # dmask = (g.df_priceconversion_data[g.df_priceconversion_data['Timestamp']== dfline['Date']])
    # g.quote_price = dmask.iloc[0]['Close']
    g.quote_price = dfline['Close']


    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    rs = binance_orders_v2(order)  # * BUY
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
    # write_val_to_file(g.coverprice, "/tmp/_insufficient_funds")


    # ! >>>>>>> [process_buy_v2:1] archive

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
    g.buy_count += 1
    str = []
    str.append(f"{g.buy_count:>4}:#[{g.gcounter:5d}]")
    # str.append(f"[{order['order_time']}]")

    if g.cvars['convert_price']:
        ts = list(g.ohlc_conv[(g.ohlc_conv['Date'] == order['order_time'])]['Close'])[0]
    else:
        ts = order['order_time'][0]

    cmd = f"UPDATE orders{g.runlevel} set SL = '{g.buymode}' where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    order_cost = toPrec("cost",order['size'] * BUY_PRICE)

    now_hms = datetime.now()
    sts = f"{now_hms.hour:02}:{now_hms.minute:02}:{now_hms.second:02}"
    # str.append(f"[{ts}]")
    str.append(f"[{order['order_time']}][L{g.runlevel}]")
    # * check if the buy test is perf based
    test_test = g.cvars[g.datatype]['testpair'][0]
    if test_test.find("perf") != -1 :
        try:
            str.append(f"[R:{g.rootperf[g.tm][g.bsig[g.tm]]['avg_pffd']:5.4f}]")
        except:
            pass
    # str.append(Fore.RED + f"Hold [{g.buymode}] " + Fore.CYAN + f"({g.BASE}){order['size']} @ ({g.QUOTE}){BUY_PRICE} = ({g.QUOTE}){order_cost}" + Fore.RESET)
    str.append(Fore.CYAN + f" BUY: ({g.BASE}){order['size']} @ ({g.QUOTE}){toPrec('price',BUY_PRICE)} = ({g.QUOTE}){toPrec('price',order_cost)}" + Fore.RESET)
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"({g.QUOTE}){g.avg_price}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"COV: " + Fore.CYAN + Style.BRIGHT + f"({g.QUOTE}){g.coverprice}" + Style.RESET_ALL)
    str.append(Fore.RED + f"Fee: " + Fore.CYAN + f"({g.QUOTE}){g.est_buy_fee}" + Fore.RESET)
    str.append(Fore.RED + f"QTY: " + Fore.CYAN + f"{g.subtot_qty}" + Fore.RESET)

    nbp = get_next_buy_price(
        state_r('last_buy_price'),
        g.next_buy_increments,
        state_r('curr_run_ct')
    )
    str.append(Fore.RED + f"NXT: " + Fore.CYAN + f"{toPrec('price',nbp)}" + Fore.RESET)

    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    # print(g.cfile_states_str)
    print(iline, flush=True)

    #! JWFIX create string functions like, also, change == to find for 'BUY_perf'

    botstr = ""
    botstr += f"R:{g.rootperf[g.tm][g.bsig[g.tm][:-1]]}" if g.cvars[g.datatype]['testpair'][0] == "BUY_perf" else ""
    # botstr += f"|H[{g.buymode}] {order['size']} @ ${BUY_PRICE} = ${order_cost}"
    botstr += f" {order['size']} @ ${toPrec('price',BUY_PRICE)} = ${toPrec('price',order_cost)}"
    botstr += f"|Q:{g.subtot_qty}"

    botmsg(f"__{botstr}__")
    log2file(iline, "ansi.txt")
    state_wr("open_buyscansell", True)
    return BUY_PRICE

def process_sell_v2(**kwargs):

    if g.display:
        g.facecolor = "black"

    SELL_PRICE = kwargs['CLOSE']
    df = kwargs['df']
    dfline = kwargs['dfline']

    if isfile(f"_next_sell_price{g.runlevel}"):
        SELL_PRICE = float(read_val_from_file(f"_next_sell_price{g.runlevel}"))
        deletefile(f"_next_sell_price{g.runlevel}")

    # * bounce of current BASE-BTC bal is 0
    if g.cvars['testnet'] and not g.cvars['offline']:
        g.subtot_qty = b.get_balance(base=g.BASE)['total']
        if g.subtot_qty == 0:
            return SELL_PRICE

    # * reset to original limits
    g.long_buys = 0
    g.dstot_Dadj = 0
    g.since_short_buy = 0
    g.short_buys = 0
    # * all cover costs incl sell fee were calculated in buy
    g.deltatime = (g.ohlc['Date'][-1] - g.session_first_buy_time).total_seconds() / 86400

    # * first get latest conversion price
    g.conversion = get_last_price(g.spot_src)

    g.cooldown = 0  # * reset cooldown
    g.buys_permitted = True  # * Allows buys again
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
    order["type"] = "market"
    order["side"] = "sell"
    order["size"] = toPrec("amount", g.subtot_qty)
    order["price"] = toPrec("price",SELL_PRICE)
    order["stop_price"] = SELL_PRICE
    order["limit_price"] = SELL_PRICE
    order["pair"] = g.cvars["pair"]
    order["state"] = "submitted"
    order["order_time"] = f"{dfline['Date']}"
    order["uid"] = g.uid
    state_wr("order", order)

    # dmask = (g.df_priceconversion_data[g.df_priceconversion_data['Timestamp']== dfline['Date']])
    # g.quote_price = dmask.iloc[0]['Close']
    g.quote_price = dfline['Close']

    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
    rs = binance_orders_v2(order)  # * SELL v2
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

    cmd = f"UPDATE orders{g.runlevel} set mxint = {g.margin_interest_cost}, mxinttot={g.total_margin_interest_cost} where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # * calc running total (incl fees)
    g.running_total = toPrec("price", get_running_bal(version=3, ret='one'))
    # waitfor()
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
    g.running_buy_fee = toPrec("price", g.subtot_cost * g.cvars['buy_fee'])
    g.est_sell_fee = toPrec("price", g.subtot_cost * g.cvars['sell_fee'])
    sess_gross = toPrec("price", (SELL_PRICE - g.avg_price) * g.subtot_qty)
    sess_net = toPrec("price", sess_gross - (g.running_buy_fee + g.est_sell_fee))


    g.sess_tot = float(read_val_from_file("_sess_tot")) + sess_net
    # * needs to be here because sess_tot not yet defined
    cmd = f"UPDATE orders{g.runlevel} SET stot = '{g.sess_tot}' where uid='{order['uid']}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()
    if g.DD:
        DDp(f"$┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        DDp(f"$┃[{g.gcounter}] SESS_TOT: LEVEL: {g.runlevel} {truncate(g.sess_tot, 5)} = {truncate(float(read_val_from_file('_sess_tot')),5)} (sess_tot) + {sess_net} (sess_net)")
        DDp(f"$┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    write_val_to_file(g.sess_tot,"_sess_tot")

    total_fee = toPrec("price", g.running_buy_fee + g.est_sell_fee)
    g.adjusted_covercost = toPrec("price", (total_fee * (1 / g.subtot_qty)) + g.margin_interest_cost)
    g.coverprice = toPrec("price", g.adjusted_covercost + g.avg_price)

    g.total_reserve = toPrec("amount", (g.capital * g.this_close))
    g.pct_cap_return = toPrec("amount", (
            g.running_total / (g.total_reserve)))  # ! JWFIX (sess_net / (g.cvars['reserve_cap'] * SELL_PRICE))

    _reserve_seed = g.cvars[g.datatype]['reserve_seed']
    g.pct_capseed_return = toPrec("amount", (
            g.running_total / (_reserve_seed * g.this_close)))

    # * update DB with pct
    cmd = f"UPDATE orders{g.runlevel} set pct = {g.pct_return}, cap_pct = {g.pct_cap_return} where uid = '{g.uid}' and session = '{g.session_name}'"
    threadit(sqlex(cmd)).run()

    # ! >>>>>>> [process_sell_v2:1] archive # print to console
    # g.dtime = (timedelta(seconds=int((get_now() - g.last_time) / 1000)))
    g.sell_count += 1
    str = []
    str.append(f"    ")
    str.append(f"#[{g.gcounter:5d}]")
    str.append(f"[{order['order_time']}][L{g.runlevel}]")
    _soldprice = toPrec("price", g.subtot_qty * SELL_PRICE)
    str.append(Fore.GREEN + f"SOLD: " + f"({g.BASE}){order['size']} @ ({g.QUOTE}){toPrec('price',SELL_PRICE)} = ({g.QUOTE}){_soldprice}")
    str.append(Fore.GREEN + f"AVG: " + Fore.CYAN + Style.BRIGHT + f"({g.QUOTE}){g.avg_price}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"Fee: " + Fore.CYAN + Style.BRIGHT + f"({g.QUOTE}){g.est_sell_fee}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessGross: " + Fore.CYAN + Style.BRIGHT + f"${sess_gross}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessFee: " + Fore.CYAN + Style.BRIGHT + f"({g.QUOTE}){total_fee}" + Style.RESET_ALL)
    str.append(Fore.GREEN + f"SessNet: " + Fore.CYAN + Style.BRIGHT + f"({g.QUOTE}){sess_net}/{toPrec('price',g.sess_tot)}" + Style.RESET_ALL)
    str.append(Fore.RESET)
    iline = str[0]
    for s in str[1:]:
        iline = f"{iline} {s}"
    print(iline)
    log2file(iline, "ansi.txt")

    g.cap_seed = toPrec("amount", g.cap_seed + (sess_net / g.this_close))
    _margin_x = g.cvars[g.datatype]['margin_x']
    g.capital = toPrec("amount", g.cap_seed * _margin_x)
    pct = g.overall_pct/100
    write_val_to_file(pct,f"_pct{g.runlevel}") # * save pct growth to calc compound g.purch_qty

    # print(g.df_priceconversion_data)


    def make_botstr(order,SELL_PRICE, _soldprice,binlive):
        botstr = f"{g.sell_count}:"
        botstr += f"Sold {order['size']} @ ${SELL_PRICE} = ${_soldprice}"
        if g.QUOTE == "BTC":
            botstr += f"|CAP:{g.capital} (${toPrec('price',g.capital * g.quote_price)})"
        else:
            botstr += f"|CAP:{g.capital})"
        botstr += f"|Pr:({g.QUOTE}){toPrec('price',binlive)}"
        return botstr

    log2file(iline, "ansi.txt")

    # * reset average price
    g.avg_price = float("Nan")
    g.bsuid = g.bsuid + 1
    g.subtot_qty = 0

    def make_capamtstr(order):
        # * set binlive to running total as default
        binlive = g.running_total
        # * save noew USDT balace to file
        src='DB'
        if not g.cvars['offline']:
            src="LI"
            balances = b.get_balance()
            binlive = balances[g.QUOTE]['total'] - g.opening_price
            cmd = f"UPDATE orders{g.runlevel} SET binlive = {binlive} where uid='{order['uid']}' and session = '{g.session_name}'"
            threadit(sqlex(cmd)).run()

        str = []
        str.append(f"{Lb(g.runlevel)}")
        str.append(f"{g.sell_count}:[{dfline['Date']}][L{g.runlevel}]")
        str.append(f"({g.session_name})")
        str.append(f"CAP: ({g.BASE})" + Fore.BLACK + Style.BRIGHT + f"{g.capital} {truncate(pct,2)}%" + Style.NORMAL)
        qval = toPrec('price', g.sess_tot) #binlive)

        # g.overall_pct = truncate(((qval/SELL_PRICE)*100) /(g.cdata['runlevels']*g.cdata['maxbuys']),2)
        g.overall_pct = truncate((qval/SELL_PRICE)*100,2)

        str.append(f"{src} Pr:" + Fore.BLACK + Style.BRIGHT + f" ({g.QUOTE})L{g.runlevel}:{qval} ({g.BASE})STOT:{g.overall_pct}%" + Style.NORMAL)
        str.append(f"{Back.RESET}{Fore.RESET}")

        iline = str[0]
        for s in str[1:]:
            iline = f"{iline} {s}"
        return [iline,binlive]

    _str = make_capamtstr(order)
    print(_str[0])
    botmsg(f"**{make_botstr(order,SELL_PRICE,_soldprice,_str[1])}**")
    # + --------------------------------------------------------

    g.purch_qty = g.initial_purch_qty

    return SELL_PRICE

def trigger(ax):
    cols = g.ohlc['ID'].max()
    g.current_close = g.ohlc.iloc[len(g.ohlc.index) - 1]['Close']

    if g.showdates:
        if g.showeach:
            end = "\n"
        else:
            end = "\r"
        g.now_time = get_now()
        sd = g.ohlc.iloc[len(g.ohlc.index) - 1]['Date']
        dtme = g.now_time-g.last_time
        g.last_time = g.now_time
        g.override = (g.override + dtme)

        # print(f"[{g.gcounter}] ms:[{dtme}] avg:[{int(g.override/g.gcounter)}] {sd} ",end=end)
        print(f"#[{g.gcounter}] $[{toPrec('price',g.current_close):>8}] {sd}                                   ",end=end)


    def tfunc(dfline, **kwargs):
        action = kwargs['action']
        df = kwargs['df']
        g.idx = dfline['ID']
        CLOSE = dfline['Close']


        # + -------------------------------------------------------------------
        # + BUY
        # + -------------------------------------------------------------------
        is_a_buy = True
        is_a_sell = True

        # * if "_ins_funds" L1 can buy
        # print(f">>>>> SEARCHING FOR : [{g.tmpdir}/_insufficient_funds{g.runlevel-1}]")

        # * if parent has insufficient fund, child can buy
        if isfile(f"_insufficient_funds{g.runlevel-1}"):
            g.Lx_canbuy = True
        # * but if parent has insufficient funds, parent can't buy until after it sells
        if isfile(f"_insufficient_funds{g.runlevel}"):
            g.Lx_canbuy = False


        if action == "buy":
            if g.idx == cols:  # * idx is the current index of row, cols is max rows... so only when arrived at last row
                # * load the test class
                importlib.reload(lib_v2_tests_class)
                tc = lib_v2_tests_class.Tests(g.cvars, dfline, df, idx=g.idx)

                _testpair = g.cvars[g.datatype]['testpair']
                PASSED = tc.buytest(_testpair[0])

                is_a_buy = is_a_buy and PASSED or g.external_buy_signal
                is_a_buy = is_a_buy and g.buys_permitted  # * we haven't reached the maxbuy limit yet
                # * BUY is approved, so check that we are not runnng hot
                g.uid = uuid.uuid4().hex

                # * make sure we have enough to cover

                # * if only 'maxbuys' elemts in pqty list, this will crash wje longbuys > maxbuys
                # * As the sum of maxbuys elemts is assumed to equal capotal, we just skip this error
                try:
                    checksize = g.subtot_qty + g.cdata['pqty'][g.long_buys]
                    havefunds = checksize <= g.capital   #g.reserve_cap

                    # b.Eprint(f"{g.reserve_cap}, {g.capital}")
                except Exception as e:
                    havefunds = False
                # print(f"+++++++  long_buys: {g.long_buys}    PQTY: {g.cdata['pqty'][g.long_buys]}")
                # can_cover = True
                # print(f"havefuns = {checksize} < {g.reserve_cap} ")
                if not havefunds:
                    nfdh = ""
                    if g.nofunds_date_from:
                        tdelta =  dfline['Date'] - g.nofunds_date_from
                        nfdh = int((tdelta.total_seconds()/60/60/25)*10)/10
                        g.max_nofunds = max(g.max_nofunds,nfdh)
                    # can_cover = False
                    sd = g.ohlc.iloc[len(g.ohlc.index) - 1]['Date']
                    sd_str = sd.strftime("%Y-%m-%d %H:%M:%S")
                    if g.DD:
                        DDp(f"|≡≡≡≡≡≡≡≡≡≡≡≡≡≡|{g.gcounter}|{toPrec('price',g.current_close):>9}|{nfdh}|{g.max_nofunds}|{sd}|f'max_buys' limit of {g.maxbuys} reached|")
                        DDp(f"CURRENT RUNLEVEL: [{g.runlevel}]")

                    # * parent process creates "_ins_funds" file with out of money
                    # *Saves cover cost to file so L1 knows when to exit
                    # if g.runlevel == 0:
                    write_val_to_file(g.coverprice,f"_insufficient_funds{g.runlevel}")
                    cmd = f"unbuffer ./v2.py -y -D -d -n -L {g.runlevel+1} -p {g.coverprice} -C {g.gcounter} -c config_backtest_ETHBTC.toml"
                    if g.DD:
                        DDp(f"@┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        DDp(f"@┃NO MORE BUYS AVAILABLE - EXITING LEVEL:[{g.runlevel}]")
                        DDp(f"@┃CREATING 'XSELL{g.runlevel}'")
                        DDp(f"@┃[{g.gcounter}] SPAWNNG NEW PROCESS: level:[{g.runlevel+1}] coverprice:[{g.coverprice}] gcounter:[{g.gcounter}]")
                        DDp(f"@┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    # print(cmd)
                    touch(f"XSELL{g.runlevel}")
                    os.system(cmd)

                    g.counterpos = int(read_val_from_file(f'_counterpos{g.runlevel}'))
                    if g.DD:
                        DDp(f"#┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                        DDp(f"#┃RETURNED FROM {g.runlevel+1} TO {g.runlevel} - XSELL{g.runlevel} IS ON")
                        DDp(f"#┃LAST counterpos:  {g.counterpos}")
                        DDp(f"#┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    g.gcounter += g.counterpos


                else:
                    # if g.runlevel == 0:
                    #     if os.path.isfile("/tmp/_insufficient_funds"):
                    #         os.remove("/tmp/_insufficient_funds")
                    g.nofunds_date_from = dfline['Date'] # * last knows good date

                is_a_buy = is_a_buy and havefunds# or can_cover)
                is_a_buy = is_a_buy and (g.gcounter >= g.cooldown and g.gcounter > 12)

                if g.runlevel > 0:
                    # print(g.Lx_canbuy)
                    is_a_buy = is_a_buy and g.Lx_canbuy

                # print(f"[{g.runlevel}],[{is_a_buy}],[{g.Lx_canbuy}]")

                # if g.runlevel == 1:
                #     if os.path.isfile("_insufficient_funds"):
                #         is_a_buy = is_a_buy and True
                #     else:
                #         is_a_buy = is_a_buy and False

                # * wait until there is a full set of data to analyse
                # is_a_buy = is_a_buy and g.gcounter > g.cvars['datawindow']

                if is_a_buy:
                    # print("XXXXX")
                    # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
                    if g.buymode == 'S':
                        _short_purch_qty = g.cvars[g.datatype]['short_purch_qty']
                        g.purch_qty = _short_purch_qty

                    if g.buymode == 'L':
                        _long_purch_qty = g.initial_purch_qty
                        # g.purch_qty = _long_purch_qty * g.mult ** g.long_buys
                        padj = 1+(float(read_val_from_file(f"_pct{g.runlevel}",default=0)))/g.cdata['maxbuys']
                        #padj = 1+(float(read_val_from_file(f"_pct{g.runlevel}",default=0)))
                        # padj = 1
                        # g.purch_qty = g.cdata['pqty'][g.long_buys] * padj
                        g.purch_qty = g.capital/g.cdata['maxbuys']
                        # b.Eprint(f"{g.purch_qty}, {g.capital}, {g.cdata['maxbuys']}, {g.cdata}")

                        # print(">>>>>>",g.purch_qty,g.cdata['pqty'][g.long_buys],g.long_buys)

                        if g.DD:
                            b.Eprint(f"padj:[{padj}]    g.purch_qty: [{g.purch_qty}]         ")


                        # print(g.initial_purch_qty, g.purch_qty)

                    # ! buymode 'X' inherits from either S or L, whichever is current

                        # * set cooldown by setting the next gcounter number that will freeup buys
                        # ! cooldown is calculated by adding the current g.gcounter counts and adding the g.cooldown
                        # ! value to arrive a the NEXT g.gcounter value that will allow buys.
                        # ! g.cooldown holds the number of buys
                        # g.cooldown = g.gcounter + (g.cvars['cooldown_mult'] * (g.long_buys + 1))
                    state_wr("purch_qty", g.purch_qty)

                    BUY_PRICE = process_buy_v2(ax=ax, CLOSE=CLOSE, df=df, dfline=dfline)
                    # * update state file
                    state_wr("purch_qty", g.purch_qty)
                    g.last_side = "buy"

                # + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

                else:
                    BUY_PRICE = float("Nan")

            else:
                BUY_PRICE = float("Nan")
            return BUY_PRICE

        # + -------------------------------------------------------------------
        # + SELL
        # + -------------------------------------------------------------------
        if action == "sell":

            if g.idx == cols and state_r("open_buyscansell"):
                # * first we check is we need to apply stop-limit rules
                limitsell = False
                # if CLOSE <= g.stoplimit_price and g.maxbuys == 1:
                #     print(f"STOP LIMIT OF {g.stoplimit_price}!")
                #     limitsell = True
                #     g.external_sell_signal = True
                # * next we check if if we have reached any sell conditions

                importlib.reload(lib_v2_tests_class)
                tc = lib_v2_tests_class.Tests(g.cvars, dfline, df, idx=g.idx)

                _testpair = g.cvars[g.datatype]['testpair']
                PASSED = tc.selltest(_testpair[1])
                is_a_sell = is_a_sell and PASSED or g.external_sell_signal
                # if g.runlevel == 1:
                g.Lx_canbuy = False

                if is_a_sell:
                    g.uid = uuid.uuid4().hex
                    if limitsell:
                        SELL_PRICE = process_sell_v2(ax=ax, CLOSE=g.stoplimit_price, df=df, dfline=dfline)
                        g.stoplimit_price = 1e-10
                    else:
                        SELL_PRICE = process_sell_v2(ax=ax, CLOSE=CLOSE, df=df, dfline=dfline)
                    # os.system(f"touch {g.tmpdir}/_sell")
                    g.adjusted_covercost = 0
                    g.running_buy_fee = 0
                    update_db_tots()  # * update 'fintot' and 'runtotnet' in db
                    g.last_side = "sell"

                    # * if "_ins_funds", L1 can continue to bye, otherwise exit.
                    if g.runlevel > -1:
                        g.Lx_canbuy = False
                        if isfile(f"_insufficient_funds{g.runlevel-1}"):
                            g.Lx_canbuy = True
                            exit_on_val = float(read_val_from_file(f"_insufficient_funds{g.runlevel-1}"))
                            # print(f">>>>> {SELL_PRICE} >= L0 coverprice of {exit_on_val} ({SELL_PRICE >= exit_on_val})")
                            if SELL_PRICE >= exit_on_val:
                                if g.DD:
                                    DDp(f"+┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                                    DDp(f"+┃[{g.gcounter}] EXIT AND SELL:(L{g.runlevel}) CHILD PRICE ({SELL_PRICE}) >= PARENT PRICE ({exit_on_val}) COVER COST ")
                                    DDp(f"+┃SAVING FINAL g.counter [{g.gcounter}] TO [_counterpos{g.runlevel-1}]")
                                    DDp(f"+┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                                write_val_to_file(g.gcounter,f"_counterpos{g.runlevel-1}")
                                # print(f"SAVED /tmp/_counterpos{g.runlevel-1} = {g.gcounter}")
                                deletefile(f"_insufficient_funds{g.runlevel-1}")
                                # print(f"********************** EXITING L{g.runlevel} ***********************")
                                # waitfor()
                                DDp(f" <<<< ─────────────────────────────────────────────────────────────────────────────────────── [{g.runlevel}] ─────", tabs=False)

                                exit()


                else:
                    SELL_PRICE = float("Nan")
            else:
                SELL_PRICE = float("Nan")

            return SELL_PRICE
        return float("Nan")

    if len(g.ohlc) != len(g.df_buysell.index):
        waitfor([f"End of data (index mismatch.  expecting {len(g.ohlc)}, got {len(g.df_buysell.index)})"])

    g.ohlc['ID'] = range(len(g.ohlc))
    g.df_buysell['ID'] = range(len(g.ohlc))

    g.ohlc["bb3avg_buy"] = float("Nan")
    g.ohlc["bb3avg_sell"] = float("Nan")

    g.df_buysell = g.df_buysell.shift(periods=1)

    try:
        g.df_buysell.index = pd.DatetimeIndex(pd.to_datetime(g.df_buysell['Timestamp'], unit=g.units))
    except:
        g.df_buysell.index = pd.DatetimeIndex(pd.to_datetime(g.df_buysell['Timestamp']))

    g.df_buysell.index.rename("index", inplace=True)

    # ! add new data to first row
    g.ohlc['bb3avg_sell'] = g.ohlc.apply(lambda x: tfunc(x, action="sell", df=g.ohlc, ax=ax), axis=1)
    g.ohlc['bb3avg_buy'] = g.ohlc.apply(lambda x: tfunc(x, action="buy", df=g.ohlc, ax=ax), axis=1)

    state_wr("avgprice", g.avg_price),
    state_wr("coverprice", g.avg_price + g.adjusted_covercost),
    state_wr("buyunder", g.next_buy_price),

    if g.avg_price > 0 and g.display:
        if g.display:
            ax.axhline(
                g.avg_price,
                color=g.cvars['styles']['avgprice']['color'],
                linewidth=g.cvars['styles']['avgprice']['width'],
                alpha=g.cvars['styles']['avgprice']['alpha']
            )
            ax.axhline(
                g.avg_price + g.adjusted_covercost,
                color=g.cvars['styles']['coverprice']['color'],
                linewidth=g.cvars['styles']['coverprice']['width'],
                alpha=g.cvars['styles']['coverprice']['alpha']
            )
            if g.next_buy_price < 1000000 and g.next_buy_price > 0:
                ax.axhline(
                    g.next_buy_price,
                    color=g.cvars['styles']['buyunder']['color'],
                    linewidth=g.cvars['styles']['buyunder']['width'],
                    alpha=g.cvars['styles']['buyunder']['alpha']
                )

    tmp = g.df_buysell.iloc[::-1].copy()  # ! here we have to invert the array to get the correct order

    bStmp = tmp[tmp['mclr'] == 0]
    bLtmp = tmp[tmp['mclr'] == 1]
    bCtmp = tmp[tmp['mclr'] == 2]

    if g.cvars['save']:
        save_df_json(bLtmp, f"{g.tmpdir}/_bLtmp.json")
        save_df_json(bStmp, f"{g.tmpdir}/_bStmp.json")  # ! short
        save_df_json(bCtmp, f"{g.tmpdir}/_bCtmp.json")  # ! short

    # * plot colored markers

    if g.display:
        ax.plot(
            bStmp['buy'],
            color=g.cvars['buy_marker']['S']['color'],
            markersize=g.cvars['buy_marker']['S']['size'],
            alpha=g.cvars['buy_marker']['S']['alpha'],
            linewidth=0,
            marker=6
        )
        ax.plot(
            bLtmp['buy'],
            color=g.cvars['buy_marker']['L']['color'],
            markersize=g.cvars['buy_marker']['L']['size'],
            alpha=g.cvars['buy_marker']['L']['alpha'],
            linewidth=0,
            marker=6
        )
        ax.plot(
            bCtmp['buy'],
            color=g.cvars['buy_marker']['X']['color'],
            markersize=g.cvars['buy_marker']['X']['size'],
            alpha=g.cvars['buy_marker']['L']['alpha'],
            linewidth=0,
            marker=6
        )
        ax.plot(
            tmp['sell'],
            color=g.cvars['buy_marker']['sell']['color'],
            markersize=20,
            alpha=1.0,
            linewidth=0,
            marker=7
        )

    # * aet rid of everything we are not seeing
    g.df_buysell = g.df_buysell.head(len(g.ohlc))

    return
