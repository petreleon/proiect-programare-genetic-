# Optimizare Strategie de Tranzacționare folosind Programarea Genetică

Acest proiect se axează pe utilizarea programării genetice pentru a optimiza o strategie de tranzacționare bazată pe diferiți indicatori tehnici.

## Descriere

Acest script Python se conectează la API-ul Binance pentru a prelua datele istorice ale prețurilor pentru un anumit simbol (în acest caz, 'BTCUSDT'). Apoi, folosește programarea genetică pentru a găsi cea mai bună combinație de parametri pentru o strategie de tranzacționare bazată pe indicatorii tehnici MACD, SMA, RSI și Bollinger Bands.

## Utilizare

Pentru a rula acest script, veți avea nevoie de chei API Binance, pe care le puteți introduce într-un fișier `.env`. 

## Detalii Implementare

Algoritmul genetic caută cea mai bună combinație de parametri pentru indicatorii tehnici. Încearcă diferite combinații și evaluează fiecare combinație pe baza unei funcții de potrivire (fitness function). Această funcție calculează cât de "bună" este o combinație de parametri, pe baza ratei de câștig a strategiei de tranzacționare.

După ce algoritmul a găsit cea mai bună soluție, aceasta este utilizată pentru a efectua un backtest pe datele istorice. Acest proces verifică performanța strategiei de tranzacționare pe datele istorice pentru a vedea cum s-ar fi comportat în trecut.

În final, strategia optimizată este testată pe un set de date noi pentru a vedea cum performează pe datele care nu au fost folosite în procesul de optimizare.

## Concluzie

Prin utilizarea programării genetice, acest script poate găsi cea mai bună combinație de parametri pentru o strategie de tranzacționare, maximizând astfel potențialul de profit.

## Rezultate

```Start                     2023-05-10 16:00:00
End                       2023-06-10 15:00:00
Duration                     30 days 23:00:00
Exposure Time [%]                   34.274194
Equity Final [$]                  104614.0812
Equity Peak [$]                   107168.8412
Return [%]                           4.614081
Buy & Hold Return [%]               -9.070735
Return (Ann.) [%]                   67.282339
Volatility (Ann.) [%]              242.343964
Sharpe Ratio                         0.277632
Sortino Ratio                        1.630422
Calmar Ratio                         2.520115
Max. Drawdown [%]                  -26.698127
Avg. Drawdown [%]                   -7.148164
Max. Drawdown Duration       23 days 16:00:00
Avg. Drawdown Duration        4 days 23:00:00
# Trades                                    9
Win Rate [%]                        33.333333
Best Trade [%]                       4.809619
Worst Trade [%]                     -1.202405
Avg. Trade [%]                       0.190398
Max. Trade Duration           3 days 13:00:00
Avg. Trade Duration           1 days 04:00:00
Profit Factor                        1.265942
Expectancy [%]                        0.21318
SQN                                  0.165959
_strategy                       TradeStrategy
_equity_curve                             ...
_trades                      Size  EntryBa...
dtype: object
```
