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
        #!! self.LOWERCLOSE = dfl['lowerClose']
        self.DSTOT = dfl['Dstot']
        #!! self.DSTOT_LOW = dfl['Dstot_lo']
        self.DATE = dfl['Date']
        self.MAV0 = dfl['MAV0']
        self.MAV1 = dfl['MAV1']
        self.MAV2 = dfl['MAV2']
        self.ALLPHI = g.mmphi


        self.PERF5_BITS = g.cvars['perf5_bits']
        self.PERF5_SET = df.tail(self.PERF5_BITS)

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
        # print(test)#!XXX
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

    #!! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # def BUY_tvb3(self):
    #     FLAG = True
    #
    #     g.next_buy_price = o.state_r('last_buy_price')* (1 - g.next_buy_increments * (o.state_r('curr_run_ct')*2))
    #
    #     PASSED_DSTOT        = self.DSTOT < self.DSTOT_LOW
    #     PASSED_NEXTBUY      = self.CLOSE < g.next_buy_price
    #     PASSED_BELOWLOW     = self.CLOSE < self.LOWERCLOSE
    #
    #     # print("PASSED_DSTOT",PASSED_DSTOT)
    #     # print("PASSED_NEXTBUY",PASSED_NEXTBUY)
    #     # print("PASSED_BELOWLOW",PASSED_BELOWLOW)
    #
    #     PASSED_CXONEXTBUY = self.xover(df=self.df, dfl=self.dfl, trigger="Close", against=g.next_buy_price)
    #
    #     PASSED_LONGRUN      = o.state_r('curr_run_ct') > 0
    #     PASSED_SHORTRUN     = o.state_r('curr_run_ct') == 0
    #     # PASSED_INBUDGET = g.subtot_qty < g.cvars['maxbuys']  # ! g.subtot_qty is total BEFORE this purchase
    #
    #     PASSED_BASE = (PASSED_DSTOT and PASSED_NEXTBUY and PASSED_BELOWLOW) or PASSED_CXONEXTBUY
    #
    #     # if PASSED_CXONEXTBUY:
    #     #     print (">>>>>>>>>>>>>>>>>>>>>>xover here!!!")
    #
    #
    #     if g.market == "bear":
    #         FLAG = FLAG and PASSED_BASE and PASSED_LONGRUN
    #         if FLAG:
    #             g.buymode = "L"
    #             g.df_buysell['mclr'].iloc[0] = 0
    #             if PASSED_CXONEXTBUY:
    #                 g.buymode = "X"
    #                 g.df_buysell['mclr'].iloc[0] = 2
    #             g.since_short_buy = 0
    #         return FLAG
    #
    #     if g.market == "bull":
    #         FLAG = FLAG and PASSED_BASE and PASSED_SHORTRUN
    #         if FLAG:
    #             g.buymode = "S"
    #             g.short_buys += 1
    #             g.since_short_buy = 0
    #             g.df_buysell['mclr'].iloc[0] = 1
    #             if PASSED_CXONEXTBUY:
    #                 g.buymode = "X"
    #                 g.df_buysell['mclr'].iloc[0] = 2
    #             if g.short_buys == 1:
    #                 g.last_purch_qty = g.purch_qty
    #                 g.since_short_buy = 0
    #         return FLAG

    #!! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # def BUY_simp(self):
    #     FLAG = True
    #
    #     g.next_buy_price = o.state_r('last_buy_price')* (1 - g.next_buy_increments * (o.state_r('curr_run_ct')*2))
    #
    #     PASSED_NEXTBUY      = self.CLOSE < g.next_buy_price
    #     PASSED_BELOWLOW     = self.CLOSE < self.LOWERCLOSE
    #
    #     FLAG = FLAG and PASSED_NEXTBUY and PASSED_BELOWLOW
    #     if FLAG:
    #         g.buymode = "L"
    #         g.df_buysell['mclr'].iloc[0] = 0
    #         g.since_short_buy = 0
    #     return FLAG

    #!! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # def BUY_perf1_tvb3(self):
    #     FLAG = True
    #
    #     PASSED_PERF = False
    #     try:
    #         if g.rootperf[g.bsig[g.tm][:-1]] >= g.cvars['perf_filter']:
    #             PASSED_PERF = True
    #     except:
    #         pass
    #
    #     g.next_buy_price = o.state_r('last_buy_price')* (1 - g.next_buy_increments * (o.state_r('curr_run_ct')*2))
    #
    #     PASSED_DSTOT        = self.DSTOT < self.DSTOT_LOW
    #     PASSED_NEXTBUY      = self.CLOSE < g.next_buy_price
    #     PASSED_BELOWLOW     = self.CLOSE < self.LOWERCLOSE
    #
    #     # print("PASSED_DSTOT",PASSED_DSTOT)
    #     # print("PASSED_NEXTBUY",PASSED_NEXTBUY)
    #     # print("PASSED_BELOWLOW",PASSED_BELOWLOW)
    #
    #     PASSED_CXONEXTBUY = self.xover(df=self.df, dfl=self.dfl, trigger="Close", against=g.next_buy_price)
    #
    #     PASSED_LONGRUN      = o.state_r('curr_run_ct') > 0
    #     PASSED_SHORTRUN     = o.state_r('curr_run_ct') == 0
    #     # PASSED_INBUDGET = g.subtot_qty < g.cvars['maxbuys']  # ! g.subtot_qty is total BEFORE this purchase
    #
    #     PASSED_BASE = (PASSED_PERF and PASSED_DSTOT and PASSED_NEXTBUY and PASSED_BELOWLOW) or PASSED_CXONEXTBUY
    #
    #     # if PASSED_CXONEXTBUY:
    #     #     print (">>>>>>>>>>>>>>>>>>>>>>xover here!!!")
    #
    #
    #     if g.market == "bear":
    #         FLAG = FLAG and PASSED_BASE and PASSED_LONGRUN
    #         if FLAG:
    #             g.buymode = "L"
    #             g.df_buysell['mclr'].iloc[0] = 0
    #             if PASSED_CXONEXTBUY:
    #                 g.buymode = "X"
    #                 g.df_buysell['mclr'].iloc[0] = 2
    #             g.since_short_buy = 0
    #         return FLAG
    #
    #     if g.market == "bull":
    #         FLAG = FLAG and PASSED_BASE and PASSED_SHORTRUN
    #         if FLAG:
    #             g.buymode = "S"
    #             g.short_buys += 1
    #             g.since_short_buy = 0
    #             g.df_buysell['mclr'].iloc[0] = 1
    #             if PASSED_CXONEXTBUY:
    #                 g.buymode = "X"
    #                 g.df_buysell['mclr'].iloc[0] = 2
    #             if g.short_buys == 1:
    #                 g.last_purch_qty = g.purch_qty
    #                 g.since_short_buy = 0
    #         return FLAG

    #!! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # def BUY_perf1(self):
    #     FLAG = True
    #
    #     g.next_buy_price = o.state_r('last_buy_price')* (1 - g.next_buy_increments * (o.state_r('curr_run_ct')*2))
    #
    #     PASSED_NEXTBUY      = self.CLOSE < g.next_buy_price
    #     PASSED_DATE = g.last_date != self.DATE # * prevenst duped that appear in time-filtered data
    #
    #     FLAG = FLAG and PASSED_DATE and PASSED_NEXTBUY
    #
    #     try:
    #         # print(g.rootperf[g.bsig[:-1]])
    #         if g.rootperf[g.tm][g.bsig[g.tm][:-1]] >= g.cvars['perf_filter']:
    #             FLAG = FLAG and True
    #         else:
    #             FLAG = FLAG and False
    #             # print(g.bsig, g.rootperf[g.bsig[:-1]])
    #     except:
    #         FLAG = FLAG and False
    #         pass
    #
    #     if FLAG:
    #         g.buymode = "L"
    #         g.df_buysell['mclr'].iloc[0] = 0
    #         g.since_short_buy = 0
    #
    #     g.last_date = self.DATE
    #
    #     return FLAG

    #!! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # def BUY_perf3(self):
    #     FLAG = True
    #
    #     g.next_buy_price = o.state_r('last_buy_price') * (
    #                 1 - g.next_buy_increments * (o.state_r('curr_run_ct') * 2))
    #
    #     PASSED_NEXTBUY = self.CLOSE < g.next_buy_price
    #     PASSED_DATE = g.last_date != self.DATE  # * prevenst duped that appear in time-filtered data
    #
    #     FLAG = FLAG and PASSED_DATE and PASSED_NEXTBUY
    #
    #     try:
    #         # print(g.rootperf[g.bsig[:-1]])
    #         pkey = g.bsig[g.tm][:-1]  # * key is 15 bits, bsig is 16 bits, so remove last bit
    #
    #         PASSED_PERF = g.rootperf[g.tm][pkey]['perf'] >= g.cvars['perf_filter']
    #         PASSED_DELTA = g.rootperf[g.tm][pkey]['delta'] >= g.cvars['delta_filter']
    #
    #         if PASSED_PERF and PASSED_DELTA:
    #             FLAG = FLAG and True
    #         else:
    #             FLAG = FLAG and False
    #             # print(g.bsig, g.rootperf[g.bsig[:-1]])
    #     except:
    #         FLAG = FLAG and False
    #         pass
    #
    #     if FLAG:
    #         g.buymode = "L"
    #         g.df_buysell['mclr'].iloc[0] = 0
    #         g.since_short_buy = 0
    #
    #     g.last_date = self.DATE
    #
    #     return FLAG

    #!! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    # def BUY_perf4(self):
    #
    #     FLAG = True
    #
    #
    #     g.next_buy_price = o.get_next_buy_price(
    #                             o.state_r('last_buy_price'),
    #                             g.next_buy_increments,
    #                             o.state_r('curr_run_ct')
    #                         )
    #
    #     PASSED_NEXTBUY = self.CLOSE < g.next_buy_price
    #     PASSED_DATE = g.last_date != self.DATE  # * skips dupes that appear in time-filtered data
    #
    #     FLAG = FLAG and PASSED_DATE and PASSED_NEXTBUY
    #
    #     # print(FLAG,PASSED_DATE,PASSED_NEXTBUY)#!XXX
    #     try:
    #
    #         # print(g.rootperf[g.bsig[:-1]])
    #         pkey = g.bsig[g.tm]  # * key is 15 bits, bsig is 16 bits, so remove last bit
    #         # print(pkey)#!XXX
    #
    #         # o.jprint(g.rootperf[g.tm])#!XXX
    #
    #         PASSED_PFFD = g.rootperf[g.tm][pkey]['avg_pffd'] < 0
    #
    #
    #
    #         if PASSED_PFFD:
    #             FLAG = FLAG and True
    #         else:
    #             FLAG = FLAG and False
    #             # print(g.bsig, g.rootperf[g.bsig[:-1]])
    #     except Exception as e:
    #         # print("ERROR in lib_v2_ohlc->BUY_perf4()", repr(e))
    #         if int(g.bsig[g.tm]) == 0:
    #             return True
    #         FLAG = FLAG and False
    #
    #     if FLAG:
    #         g.buymode = "L"
    #         g.df_buysell['mclr'].iloc[0] = 0
    #         g.since_short_buy = 0
    #
    #     g.last_date = self.DATE
    #
    #     return FLAG

    # ! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def BUY_perf5(self):
        FLAG = True

        # p5specs_8 = o.get_perf5_specs(self.PERF5_SET, 8)
        # p5specs_16 = o.get_perf5_specs(self.PERF5_SET, 16)
        # p5specs_32 = o.get_perf5_specs(self.PERF5_SET, 32)
        # p5specs_64 = o.get_perf5_specs(self.PERF5_SET, 64)
        p5specs_x = o.get_perf5_specs(self.PERF5_SET, g.cdata['perf5_buy_length'])

        g.next_buy_price = o.get_next_buy_price(
                                o.state_r('last_buy_price'),
                                g.next_buy_increments,
                                o.state_r('curr_run_ct')
                            )
        PASSED_LOWZONE = True #self.MAV0 < self.MAV2
        PASSED_ALLPHI =  self.CLOSE < self.ALLPHI # ( buy when close in lower part of range
        PASSED_DSTOT = True #self.DSTOT <= -0.0

        PASSED_P5SPEC_HIGH = (
                True
                # and p5specs_8['sd'] > 0
                # and p5specs_16['sd'] > 0
                # and p5specs_32['sd'] > 0
                # and p5specs_64['sd'] > 0
                and p5specs_x['sd'] > g.cdata['perf5_buy_greaterthan']
        )

        PASSED_LOWER_THAN_LAST  = self.CLOSE < o.state_r('last_buy_price')
        PASSED_NEXTBUY          = self.CLOSE < g.next_buy_price
        PASSED_DATE            = g.last_date != self.DATE  # * skips dupes that appear in time-filtered data

        stat = F"""
        PASSED_DATE            = {PASSED_DATE}
        PASSED_NEXTBUY         = {PASSED_NEXTBUY}
        PASSED_LOWER_THAN_LAST = {PASSED_LOWER_THAN_LAST}
        PASSED_P5SPEC_HIGH     = {PASSED_P5SPEC_HIGH}
        PASSED_LOWZONE         = {PASSED_LOWZONE}
        PASSED_ALLPHI          = {PASSED_ALLPHI}
        PASSED_DSTOT           = {PASSED_DSTOT}
        p5specs > p5limit      = {p5specs_x['sd']} > {g.cdata['perf5_buy_greaterthan']}
        """

        # print(stat)
        # print(f">>>[{p5specs_x['sd']} > {g.cdata['perf5_buy_greaterthan']}<<<")

        FLAG = (
                FLAG
                and PASSED_DATE
                and PASSED_NEXTBUY
                and PASSED_LOWER_THAN_LAST
                and PASSED_P5SPEC_HIGH
                and PASSED_LOWZONE
                and PASSED_ALLPHI
                and PASSED_DSTOT
        )

        if FLAG:
            g.buymode = "L"
            g.df_buysell['mclr'].iloc[0] = 0
            g.since_short_buy = 0
            g.p5sd =  p5specs_x['sd']
            # print('BUY :',p5specs_x)



        g.last_date = self.DATE

        return FLAG

    # ! ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def BUY_tvb3_stream(self):
        FLAG = True

        g.next_buy_price = o.state_r('last_buy_price')* (1 - g.next_buy_increments * (o.state_r('curr_run_ct')*2))
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

        # * ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓

    def SELL_tvb3(self):
        FLAG = True

        # * automatically sell if 1% jump
        if self.CLOSE >= g.coverprice * 1.009:
            return True

        FLAG = FLAG and self.CLOSE >= g.coverprice

        # print(">>>>>>>>>>>> ",self.DATE, self.CLOSE,g.coverprice, self.CLOSE >= g.coverprice)

        # if g.long_buys < 2:
        #     p5specs_x = o.get_perf5_specs(self.PERF5_SET, 27)
        #     PASSED_P5SPEC_LOW = (
        #             True
        #             and p5specs_x['sd'] < 0
        #     )
        #     FLAG = FLAG and PASSED_P5SPEC_LOW

        # print(f">>>>>   {self.CLOSE} / {g.coverprice}")
        return FLAG

   # * ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
    def SELL_perf5(self):
        FLAG = True

        x = ((self.CLOSE-g.coverprice)/g.coverprice)*100
        g.selldelta =o.truncate(x,2)

        # * automatically sell if 1% jump
        # if self.CLOSE >= g.coverprice * 1.01:
        if self.CLOSE >= g.coverprice * g.cdata['sell_at']:
            g.p5sd = "x"
            return True


        # print(f"[[{o.truncate(x,2)}]]")
        FLAG = FLAG and self.CLOSE >= g.coverprice
        # print(">>>>>>>>>>>> ",self.DATE, self.CLOSE,g.coverprice, self.CLOSE >= g.coverprice)

        # if g.long_buys < 2:
        p5specs_x = o.get_perf5_specs(self.PERF5_SET, g.cdata['perf5_sell_length'])
        PASSED_P5SPEC_LOW = (
                True
                and p5specs_x['sd'] < g.cdata['perf5_sell_lessthan']
        )
        FLAG = FLAG and PASSED_P5SPEC_LOW

        # print(f">>>>>   {self.CLOSE} / {g.coverprice}")

        if FLAG:
            # print('SELL:',p5specs_x)
            g.p5sd =  p5specs_x['sd']

        return FLAG

