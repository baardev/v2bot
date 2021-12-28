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

        g.next_buy_price = o.state_r('last_buy_price')* (1 - g.cvars['next_buy_increments'] * (o.state_r('curr_run_ct')*2))
        # g.next_buy_price = o.state_r('last_buy_price')  *  (1 - g.cvars['next_buy_increments'])

        # inc = g.cvars['next_buy_increments']
        # ct = g.curr_run_ct + 1
        # rm = ((inc * ct)**2)/(inc * 2)
        # rm2 = math.sqrt(rm)
        # rm3 = (1-rm2)
        # g.next_buy_price = o.state_r('last_buy_price') * rm3

        # * reduce next price by 4th root of close as percentage
        # nmod = 1-(g.this_close**(1.0/4))/100
        # nmod = 1
        # g.next_buy_price = o.state_r('last_buy_price') * nmod

        if g.market == "bear":
            FLAG = FLAG and (
               self.DSTOT < self.DSTOT_LOW #g.cvars['dstot_Dadj'][g.long_buys]
               and self.CLOSE < g.next_buy_price
               and self.CLOSE < self.LOWERCLOSE
               and o.state_r('curr_run_ct') > 0
               and g.subtot_qty < g.cvars['maxbuys'] # ! g.subtot_qty is total BEFORE this purchase

            )

            if FLAG:
                g.buymode = "L"
                # g.ohlc['Type'].iloc[0] = 0
                g.df_buysell['mclr'].iloc[0] = 0
                g.since_short_buy = 0


        if g.market == "bull":
            FLAG = FLAG and (
                    self.CLOSE < self.LOWERCLOSE
                    and self.CLOSE < g.next_buy_price
                    and g.long_buys == 0
            )
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


    # * ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def SELL_tvb3(self):
        FLAG = True
        FLAG = FLAG and self.CLOSE > g.coverprice
        return FLAG

