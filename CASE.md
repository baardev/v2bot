So, my bot is working great for the most part.  There are two problems:

The bot algorithm is designed to perform to tasks.  1) Short term, (5-15 minutes) trades which realise small profits, but which are high frequency (approx 10/day on avg).  2) Long term (days to weeks) trades. 

The Short are triggered by a simple cross-under of 12pt EMA 0.1% redunction of the closing price.   Shorts are active in Bullish conditions.

The Long is determined by applying the cumulative result of a 6-band low-pass FFT (Fast Fourier Transform) that analyses the direction of the 6 cycles and triggers when all six frequencies moving down at the same time.  Longs are active in Bearish conditions.

While the Longs can bring in more profits/trade, they also serve to ensure that the Shorts can operate during a dip.  

For example, a Short is applied at $100, but the prices immediately drops, ensuring that short can’t sell at a profit until the price comes back up to >$100.  In this case, the Long is applied at ever 5% dip, and at 2x the previous size.  This brings the weighted average down significantly, making a profitable sell much more likely.

![chart-2](/home/jw/store/src/jmcap/v2bot/chart-2.png)

There are two initial problems with this algo:

1: because it shaves small profits, the fees will wipe out any gains.

2: To cover the dips, a reserve amount of capital is needed, and that reserve can get pretty large. For example, in the massive 50% dip in ETH (against BTC) in May-June '21, to cover that, if you start with a capital of 1 ETH and you double-downed every 3% drop, you’d need 126 ETH!!

The solution is to use margins. For example, 1 ETH on a 50x margin gives 50 available ETH.  Testing this against the all of 2021 (up until Dec 11), which includes the May-June 50% crash of ETH, with a 5% drop-trigger, the bot produced $5658.74 of net profits (after fees and margin interest) , which is a 22% return on the seed capital at the value of sale.. i.e. ignoring the increase in the value of ETH itself.  

The total number of transactions were 3,778, broken down by size (in ETH) below.

```
+-------------+-----------+
| count(size) | size      |
+-------------+-----------+
|        3473 |  1.000000 |
|         185 |  2.000000 |
|          77 |  3.000000 |
|          21 |  8.000000 |
|           5 | 10.000000 |
|          15 | 11.000000 |
|           1 | 32.000000 |
|           1 | 44.000000 |
+-------------+-----------+
```



![v21](/home/jw/share/v21.png)

But this creates a new problem, which is, there is no way this can be tested other than to actually do it. Back-testing and sandbox sites, like the Coinbase dev API, won't work because they don't account for slippage, nor can they do margins.  

So, I am seeing who is interested in going in on this test.  I am trying to understand what the worst-case scenario might be because:

- This algo will never sell anything a a loss, which means, it will buy the dip to bring down the sale price.  If trading between two high market-cap cryptos, then regardless of the dollar value of the cryptos, even if there is in a major crash, the two cryptos will always move up and down together, as all cryptos with significant market-cap move together.  The only scenario where it will loose money is if one, and only one, major crypto crashes, and never returns.  This algo is designed to increase the number of crypto, not necessary the number of dollars, most exposure here is the difference between ETH/BTC.
- There are fees of 0.1%. But this means that if you buy 126 ETH, the fee is $500.  
- The interest rate on margins is 0.02%/day, and that overhead has already been built into the bot's logic, so it knows to cover that cost, so the number reported is after interest and fees.  
- If you are selling a large amount of ETH at market price, like 126 ETH,  it's going to get broken into many smaller sales; if the market is going up, you make more than the bot requires, but if the market goes down, you make less.  Same idea with buying...  if you are buying 126 ETH, such a purchase will probably shift the market, pushing the price up.  For this reason, this bot can only run on a big exchange, like Binance.  It's common to see sales of > 10 ETH each second.  So the trick would be to read the order book and buy at a slightly lower volume than the sells (to try and not change the direction of the trend)