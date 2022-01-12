# from lib_v2_cvars import Cvars
import lib_v2_globals as g
import lib_v2_ohlc as o
import math

class Tests:
    def __init__(self, cvars, dfl, df, **kwargs):
        # + self.cargs = cargs
        idx = kwargs['idx']
        self.df = df
        self.dfl = dfl
        self.FLAG = True
        self.cvars = cvars

        # + - RUNTIME VARS (required)
        self.AVG_PRICE = g.avg_price
        self.CLOSE = dfl['Close']
        self.LOWERCLOSE = dfl['lowerClose']
        self.DSTOT = dfl['Dstot']
        self.DSTOT_LOW = dfl['Dstot_lo']
        self.DATE = dfl['Date']

    def xunder(self,**kwargs):
        rs = False
        df = kwargs['df']
        dfl = kwargs['dfl']
        varval = kwargs['trigger']
        refval = kwargs['against']
        current_varval = df[varval].iloc[len(df.index)-1]
        prev_varval =df[varval].iloc[len(df.index)-2]

        if prev_varval > refval and current_varval < refval:
            rs = True
        return rs

    def xover(self,**kwargs):
        rs = False
        df = kwargs['df']
        dfl = kwargs['dfl']
        varval = kwargs['trigger']
        refval = kwargs['against']
        current_varval = df[varval].iloc[len(df.index)-1]
        prev_varval =df[varval].iloc[len(df.index)-2]

        if prev_varval < refval and current_varval >= refval:
            rs = True
        return rs

    def buytest(self, test):
        g.buyfiltername = test
        call = f"self.{test}()"
        return eval(call)

    def selltest(self, test):
        g.sellfiltername = test
        call = f"self.{test}()"
        return eval(call)


    def BUY_never(self): return False
    def SELL_never(self): return False
    def BUY_always(self): return True
    def SELL_always(self): return True

    # ! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def BUY_tvb3(self):
        FLAG = True

        g.next_buy_price = o.state_r('last_buy_price')* (1 - g.cvars[g.datatype]['next_buy_increments'] * (o.state_r('curr_run_ct')*2))

        PASSED_DSTOT        = self.DSTOT < self.DSTOT_LOW
        PASSED_NEXTBUY      = self.CLOSE < g.next_buy_price
        PASSED_BELOWLOW     = self.CLOSE < self.LOWERCLOSE

        # print("PASSED_DSTOT",PASSED_DSTOT)
        # print("PASSED_NEXTBUY",PASSED_NEXTBUY)
        # print("PASSED_BELOWLOW",PASSED_BELOWLOW)

        PASSED_CXONEXTBUY = self.xover(df=self.df, dfl=self.dfl, trigger="Close", against=g.next_buy_price)

        PASSED_LONGRUN      = o.state_r('curr_run_ct') > 0
        PASSED_SHORTRUN     = o.state_r('curr_run_ct') == 0
        # PASSED_INBUDGET = g.subtot_qty < g.cvars['maxbuys']  # ! g.subtot_qty is total BEFORE this purchase

        PASSED_BASE = (PASSED_DSTOT and PASSED_NEXTBUY and PASSED_BELOWLOW) or PASSED_CXONEXTBUY

        # if PASSED_CXONEXTBUY:
        #     print (">>>>>>>>>>>>>>>>>>>>>>xover here!!!")


        if g.market == "bear":
            FLAG = FLAG and PASSED_BASE and PASSED_LONGRUN
            if FLAG:
                g.buymode = "L"
                g.df_buysell['mclr'].iloc[0] = 0
                if PASSED_CXONEXTBUY:
                    g.buymode = "X"
                    g.df_buysell['mclr'].iloc[0] = 2
                g.since_short_buy = 0
            return FLAG

        if g.market == "bull":
            FLAG = FLAG and PASSED_BASE and PASSED_SHORTRUN
            if FLAG:
                g.buymode = "S"
                g.short_buys += 1
                g.since_short_buy = 0
                g.df_buysell['mclr'].iloc[0] = 1
                if PASSED_CXONEXTBUY:
                    g.buymode = "X"
                    g.df_buysell['mclr'].iloc[0] = 2
                if g.short_buys == 1:
                    g.last_purch_qty = g.purch_qty
                    g.since_short_buy = 0
            return FLAG


    # ! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def BUY_tvb3_stream(self):
        FLAG = True

        g.next_buy_price = o.state_r('last_buy_price')* (1 - g.cvars[g.datatype]['next_buy_increments'] * (o.state_r('curr_run_ct')*2))
        if g.market == "bear":
            FLAG = FLAG and (
                (
                   self.DSTOT < self.DSTOT_LOW # ! g.cvars['dstot_Dadj'][g.long_buys]
                   and self.CLOSE < g.next_buy_price
                   and self.CLOSE < self.LOWERCLOSE
                   and o.state_r('curr_run_ct') > 0
                   and g.subtot_qty < g.cvars['maxbuys']) # ! g.subtot_qty is total BEFORE this purchase
                ) or self.xover(df=self.df, dfl=self.dfl, trigger='Close', against=g.next_buy_price
            )

            if FLAG:
                g.buymode = "L"
                g.df_buysell['mclr'].iloc[0] = 0
                g.since_short_buy = 0


        if g.market == "bull":
            FLAG = FLAG and (
                    self.CLOSE < self.LOWERCLOSE
                    and self.CLOSE < g.next_buy_price
                    and g.long_buys == 0
            ) or self.xover(df=self.df, dfl=self.dfl, trigger="Close", against=g.next_buy_price)

            if FLAG:
                g.buymode = "S"
                g.short_buys += 1
                g.since_short_buy = 0
                g.df_buysell['mclr'].iloc[0] = 1
                if g.short_buys == 1:
                    g.last_purch_qty = g.purch_qty
                    # g.purch_qty = self.cvars['first_short_buy_amt']
                    g.since_short_buy = 0

        # print(g.buymode,g.market, o.state_r('curr_run_ct'))
        # o.waitfor()
        return FLAG

    # ! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def BUY_perf(self):


        g.next_buy_price = o.state_r('last_buy_price')* (1 - g.cvars[g.datatype]['next_buy_increments'] * (o.state_r('curr_run_ct')*2))
        PASSED_NEXTBUY      = self.CLOSE < g.next_buy_price

        PASSED_DATE = g.last_date != self.DATE # * prevenst duped that appear in time-filtered data

        FLAG = True
        FLAG = FLAG and PASSED_DATE and PASSED_NEXTBUY

        try:
            # print(g.rootperf[g.bsig[:-1]])
            if g.rootperf[g.bsig[:-1]] >= g.cvars['perf_filter']:
                FLAG = FLAG and True
            else:
                FLAG = FLAG and False
                # print(g.bsig, g.rootperf[g.bsig[:-1]])
        except:
            FLAG = FLAG and False
            pass

        if FLAG:
            g.buymode = "L"
            g.df_buysell['mclr'].iloc[0] = 0
            g.since_short_buy = 0

        g.last_date = self.DATE

        return FLAG


    # * ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def SELL_tvb3(self):
        FLAG = True
        FLAG = FLAG and self.CLOSE > g.coverprice
        return FLAG

