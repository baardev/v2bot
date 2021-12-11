# from lib_v2_cvars import Cvars
import lib_v2_globals as g
import lib_v2_ohlc as o


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
        COND1 = True
        COND2 = True
        g.next_buy_price = o.state_r('last_buy_price') * (1 - 0.001 * o.state_r('current_run_count'))
        # ! SEE CONDITIONS IN AT LINE ~650 IN ohlc.py

        if g.market == "bear":
            FLAG = FLAG and (                                           # * red
               self.DSTOT < g.dstot_buy
               and self.CLOSE < g.next_buy_price
               and self.CLOSE < self.LOWERCLOSE
               # and self.xunder(trigger="Close", against=self.LOWERCLOSE, dfl=self.dfl, df=self.df)
            )
            if FLAG:
                g.buymode = "L"
                g.df_buysell['mclr'].iloc[0] = 0

        if g.market == "bull":
            FLAG = FLAG and (
                    self.CLOSE < self.LOWERCLOSE
                    # and self.CLOSE < g.next_buy_price
                    and g.long_buys == 0
            )
            if FLAG:
                g.buymode = "D"
                g.df_buysell['mclr'].iloc[0] = 1
                g.purch_qty = self.cvars['purch_pct']/100


        return FLAG


    # * ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def SELL_tvb3(self):
        FLAG = True

        # total_fee = g.running_buy_fee + g.est_sell_fee
        # covercost = total_fee * (1 / g.subtot_qty)
        # coverprice = covercost + g.avg_price

        # print(f"close: {self.CLOSE}  coverprice: {coverprice}")
        # coverprice = covercost + g.avg_price

        # FLAG = FLAG and (self.FFMAPS_DNTURN and self.FFMAPS > g.ffmaps_midline and self.CLOSE > g.coverprice)
        sellat = self.AVG_PRICE * 0.995

        FLAG = FLAG and self.CLOSE > g.coverprice #or self.DSTOT > o.cvars.get("overunder_sell"))
        # FLAG = FLAG or self.CLOSE < sellat


        return FLAG

