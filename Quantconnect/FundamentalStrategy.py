from AlgorithmImports import *
# Dynamic Stock Selection Algorithm based on Fundamental Factors
import operator
from math import ceil,floor
from itertools import groupby
from datetime import datetime, timedelta
import pandas as pd

from QuantConnect.Data.UniverseSelection import *

class BasicTemplateAlgorithm(QCAlgorithm):
    
    def __init__(self):
    # set the flag for rebalance
        self.reb = 1
    # Number of stocks to pass CoarseSelection process
        self.num_coarse = 900
    # Number of stocks to long/short
        self.num_fine = 7 #Watch out for adjustment of outliers in line 297
        self.symbols = None
        #self.value = 0
        #self.inverted=0
        self.prediction=0
        #self.currency=8.77
        self.Portfoliovalue = pd.DataFrame()

    def Initialize(self):
        self.SetCash(1000000)
        self.SetStartDate(2022,1,1)
        #self.SetEndDate(2022,2,20)
    
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.SetBenchmark('SPY')
        
        self.UniverseSettings.Resolution = Resolution.Daily
        
        self.AddUniverse(self.CoarseSelectionFunction,self.FineSelectionFunction)
        
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        self.economy_score = self.AddData(EconomyScore, "Economy_Score", Resolution.Daily).Symbol
        #self.SetAlpha(ConstantAlphaModel(InsightType.Price, InsightDirection.Up, timedelta(30)))


    # Schedule the rebalance function to execute at the begining of each week
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Tuesday, DayOfWeek.Friday),#(self.spy), #(self.spy), 
        self.TimeRules.AfterMarketOpen(self.spy,1), Action(self.rebalance))

        from System.Drawing import Color

        stockPlot = Chart('Strategy Return %')
        #self.Plot("Strategy Return %", ((self.Portfolio.TotalPortfolioValue -1000000) / 1000000)*100)
        stockPlot.AddSeries(Series('Strategy Return',SeriesType.Line, '%', Color.Green))
        self.AddChart(stockPlot)

        self.Schedule.On(self.DateRules.Every(DayOfWeek.Monday), 
                        self.TimeRules.At(10, 30),
                        self.Plotting)
 
       

    def Plotting(self):
        self.Plot("Positions", "Num", len([x.Symbol for x in self.Portfolio.Values if self.Portfolio[x.Symbol].Invested]))
        #self.Plot("Strategy Return % NOK", 'Strategy Return %', ((((self.Portfolio.TotalPortfolioValue*self.currency)-(self.Initialvalue)) / (self.Initialvalue)))*100)
        #self.Plot("Portfolio Value NOK", 'Strategy Value', ((self.Portfolio.TotalPortfolioValue)*self.currency))



    def CoarseSelectionFunction(self, coarse):
    # if the rebalance flag is not 1, return null list to save time.
        if self.reb != 1:
            return self.long 
    # make universe selection once a week
    # drop stocks which have no fundamental data or have too low prices
        selected = [x for x in coarse if (x.HasFundamentalData)
                    and x.Symbol.Value not in ["UARM", "UA"]
                    and (float(x.Price) > 10)
                    #and (x.Market == "usa")
                    and (x.DollarVolume > 1e6)]
        
        sortedByDollarVolume = sorted(selected, key=lambda x: x.DollarVolume, reverse=True)
        top = sortedByDollarVolume[:self.num_coarse]
        return [i.Symbol for i in top]

    def FineSelectionFunction(self, fine):
    # return null list if it's not time to rebalance
        if self.reb != 1:
            return self.long
          
        self.reb = 0
            
    # drop stocks which don't have the information we need.
    # you can try replacing those factor with your own factors here
    
        filtered_fine = [x for x in fine if x.OperationRatios.OperationMargin.ThreeMonths != 0
                                            #and x.OperationRatios.OperationMargin.OneYear
                                            #and x.OperationRatios.RevenueGrowth.OneYear
                                            and x.OperationRatios.RevenueGrowth.ThreeMonths != 0
                                            #and x.OperationRatios.RevenueGrowth.ThreeYears
                                            #and x.OperationRatios.AssetsTurnover.OneYear
                                            and x.OperationRatios.AssetsTurnover.ThreeMonths != 0
                                            and x.OperationRatios.EBITDAMargin.ThreeMonths != 0
                                            #and x.OperationRatios.EBITDAMargin.SixMonths
                                            #and x.OperationRatios.EBITDAMargin.OneYear
                                            and x.CompanyReference.PrimaryExchangeID in ["NYS","NAS"]
                                            #and (x.CompanyReference.CountryId == "USA")
                                            #and x.FinancialStatements.BalanceSheet.TotalEquity.TwelveMonths
                                            #and x.EarningRatios.FCFPerShareGrowth.OneYear
                                            #and x.OperationRatios.CFOGrowth.OneYear
                                            #and x.ValuationRatios.PBRatio
                                            #and x.ValuationRatios.PSRatio
                                            #and x.ValuationRatios.PCFRatio
                                            #and x.ValuationRatios.PERatio 
                                            and x.OperationRatios.ROE.ThreeMonths != 0
                                            #and x.OperationRatios.ROIC.ThreeMonths 
                                            and x.OperationRatios.ROA.ThreeMonths != 0
                                            #and x.OperationRatios.FinancialLeverage.OneYear
                                            #and x.FinancialStatements.IncomeStatement.ResearchAndDevelopment.ThreeMonths=> 0
                                            #and x.ValuationRatios.TrailingDividendYield < 0.005
                                            #and x.OperationRatios.NetIncomeGrowth.Value!=0
                                            and x.OperationRatios.StockholdersEquityGrowth.OneYear != 0
                                            and x.SecurityReference.IsPrimaryShare > 0
                                            #and (x.AssetClassification.FinancialHealthGrade!="F")
                                            #and (x.AssetClassification.FinancialHealthGrade!="E")
                                            #and x.FinancialStatements.IncomeStatement.TotalRevenue.TwelveMonths
                                            #and x.SecurityReference.SecurityType == "ST00000001"
                                            #and (x.AssetClassification.MorningstarSectorCode!= 309)
                                            and (x.AssetClassification.MorningstarSectorCode!=206)
                                            and (x.AssetClassification.MorningstarIndustryGroupCode!=31055)]
                                            #and x.OperationRatios.ROIC.OneYear != 0
                                            #and x.OperationRatios.ROIC.ThreeMonths != 0]
                                            #and (x.FinancialStatements.IncomeStatement.ResearchAndDevelopment.ThreeMonths != 0)
                                            #and (x.EarningReports.BasicAverageShares.ThreeMonths != 0)
                                            #and (x.EarningReports.BasicEPS.ThreeMonths != 0)]
        for i in filtered_fine:
        #ROA/ROE
             i.roa_ratio = (i.OperationRatios.ROA.ThreeMonths / i.OperationRatios.ROE.ThreeMonths)
        
           
                                    
    
                                        
        self.Debug('remained to select %d'%(len(filtered_fine)))
        
        # rank stocks factor
        sortedByfactor1 = sorted(filtered_fine, key=lambda x: x.OperationRatios.OperationMargin.ThreeMonths, reverse=False)
        
        sortedByfactor2 = sorted(filtered_fine, key=lambda x: x.OperationRatios.RevenueGrowth.ThreeMonths, reverse=False)
        
        sortedByfactor3 = sorted(filtered_fine, key=lambda x: x.OperationRatios.AssetsTurnover.ThreeMonths, reverse=False)
        
        
        sortedByfactor4 = sorted(filtered_fine, key=lambda x: x.OperationRatios.EBITDAMargin.ThreeMonths, reverse=False)
        
        sortedByfactor6 = sorted(filtered_fine, key=lambda x: x.OperationRatios.RevenueGrowth.ThreeYears, reverse=False)
        
        sortedByfactor7 = sorted(filtered_fine, key=lambda x: x.OperationRatios.StockholdersEquityGrowth.OneYear, reverse=False)
        
        sortedByfactor8 = sorted(filtered_fine, key=lambda x: x.OperationRatios.CFOGrowth.OneYear, reverse=False)
        
        sortedByfactor9 = sorted(filtered_fine, key=lambda x: x.OperationRatios.RevenueGrowth.OneYear, reverse=False)
        
        sortedByfactor10 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PBRatio, reverse=False)
        
        sortedByfactor11 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PSRatio, reverse=False)
        
        sortedByfactor12 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PCFRatio, reverse=False)
        
        #sortedByfactor13 = sorted(filtered_fine, key=lambda x: x.OperationRatios.EBITDAMargin.ThreeMonths, reverse=False)
        
        sortedByfactor14 = sorted(filtered_fine, key=lambda x:  x.ValuationRatios.PERatio, reverse=False)
        
        sortedByfactor15 = sorted(filtered_fine, key=lambda x: x.OperationRatios.AssetsTurnover.OneYear, reverse=False)
        
        sortedByfactor16 = sorted(filtered_fine, key=lambda x: x.OperationRatios.ROE.ThreeMonths, reverse=False)
        
        sortedByfactor17 = sorted(filtered_fine, key=lambda x: x.OperationRatios.ROIC.ThreeMonths, reverse=False)
        
        sortedByfactor18 = sorted(filtered_fine, key=lambda x: x.OperationRatios.ROA.ThreeMonths, reverse=False)
        
        sortedByfactor19 = sorted(filtered_fine, key=lambda x: x.OperationRatios.EBITDAMargin.OneYear, reverse=False)
        
        sortedByfactor20 = sorted(filtered_fine, key=lambda x: x.OperationRatios.AssetsTurnover.ThreeMonths, reverse=False)
        
        sortedByfactor21 = sorted(filtered_fine, key=lambda x: x.OperationRatios.GrossMargin.ThreeMonths, reverse=False)
        
        sortedByfactor22 = sorted(filtered_fine, key=lambda x: x.AssetClassification.SizeScore, reverse=False)
        
        sortedByfactor23 = sorted(filtered_fine, key=lambda x: x.AssetClassification.StyleScore, reverse=False)
        
        sortedByfactor24 = sorted(filtered_fine, key=lambda x: x.AssetClassification.GrowthScore, reverse=False)
        
        sortedByfactor25 = sorted(filtered_fine, key=lambda x: x.OperationRatios.TotalAssetsGrowth.Value, reverse=False) # check out
        
        #sortedByfactor26 = sorted(filtered_fine, key=lambda x: x.OperationRatios.TotalDebtEquityRatio.Value, reverse=False)
        
        #sortedByfactor27 = sorted(filtered_fine, key=lambda x: x.OperationRatios.SolvencyRatio.Value, reverse=False)
        
        sortedByfactor28 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PERatio, reverse=False)
        
        sortedByfactor29 = sorted(filtered_fine, key=lambda x: x.EarningRatios.EquityPerShareGrowth.ThreeMonths, reverse=False)
        
        sortedByfactor30 = sorted(filtered_fine, key=lambda x: x.OperationRatios.RevenueGrowth.FiveYears, reverse=False)
    
        sortedByfactor31 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PricetoEBITDA, reverse=False)
        
        sortedByfactor33 = sorted(filtered_fine, key=lambda x: x.OperationRatios.RegressionGrowthOperatingRevenue5Years.FiveYears, reverse=False)
        
        sortedByfactor34 = sorted(filtered_fine, key=lambda x: x.OperationRatios.EBITMargin.ThreeMonths, reverse=False)
        
        sortedByfactor35 = sorted(filtered_fine, key=lambda x: x.OperationRatios.GrossMargin5YrAvg.FiveYears, reverse=False)

        sortedByROARatio = sorted(filtered_fine, key=lambda x: x.roa_ratio, reverse=False)
        
        stock_dict = {}
        
        # assign a score to each stock, you can also change the rule of scoring here.
        for i,ele in enumerate(sortedByfactor1):
                margin = i
                revenue_growth3m = sortedByfactor2.index(ele)
                assets_turnover = sortedByfactor3.index(ele)
                ebitda_margin3m = sortedByfactor4.index(ele)
                revenue_growth3 = sortedByfactor6.index(ele)
                equity_growth1 = sortedByfactor7.index(ele)
                #cfgrowth = sortedByfactor8.index(ele) 
                revenue_growth1 = sortedByfactor9.index(ele)
                pb_ratio = sortedByfactor10.index(ele)
                ps_ratio = sortedByfactor11.index(ele)
                pcf_ratio = sortedByfactor12.index(ele)
                #ebitda_margin3m = sortedByfactor13.index(ele)
                ebitda_margin1 = sortedByfactor19.index(ele)
                pe_ratio = sortedByfactor14.index(ele)
                assets_turnover1yr = sortedByfactor15.index(ele)
                ROE = sortedByfactor16.index(ele)
                ROIC = sortedByfactor17.index(ele)
                ROA = sortedByfactor18.index(ele)
                gross_margin = sortedByfactor21.index(ele)
                size_score = sortedByfactor22.index(ele)
                style_score = sortedByfactor23.index(ele)
                growth_score = sortedByfactor24.index(ele)
                assets_growth = sortedByfactor25.index(ele)
                #debt_equity = sortedByfactor26.index(ele)
                #solvency_ratio = sortedByfactor27.index(ele)
                pe_growth = sortedByfactor28.index(ele)
                equity_growth = sortedByfactor29.index(ele)
                revenue_growth5 = sortedByfactor30.index(ele)
                priceebitda = sortedByfactor31.index(ele)
                revenue_growth_reg = sortedByfactor33.index(ele)
                ebit_margin = sortedByfactor34.index(ele)
                grossmarginavg = sortedByfactor35.index(ele)
                roatoroe = sortedByROARatio.index(ele)
                
                
                score = [(gross_margin)*26,
                        (revenue_growth3)*3,
                        (assets_turnover)*80,
                        (ebitda_margin3m)*30,
                        (revenue_growth3m)*145,
                        (equity_growth)*9,
                        (pe_ratio)*2,
                        (pb_ratio)*2,
                        (ps_ratio)*2,
                        (pcf_ratio)*2,
                        (size_score)*110,
                        (style_score)*10,
                        (growth_score)*5,
                        (grossmarginavg)*15,
                        (roatoroe)*5]

                score = sum(score)
                stock_dict[ele] = score

               
                
        self.Debug('Comined Score %d'%((score)))
        # sort the stocks by their scores
        self.sorted_stock = sorted(stock_dict.items(), key=lambda d:d[1],reverse=True)
        sorted_symbol = [x[0] for x in self.sorted_stock]
          

        # sort the top stocks into the long_list and the bottom ones into the short_list
        self.long = [x.Symbol for x in sorted_symbol[:self.num_fine]] # Adjust in sorted_symbol[] if you want to remove outliers or specify how many stocks in self long will be added
        self.score = score
        return self.long
        
                    
    def OnData(self, data):
        from System.Drawing import Color
       # self.Plot("Strategy Return %", 'Strategy Return', ((self.Portfolio.TotalPortfolioValue -1000000) / 1000000)*100)
       # self.Plot("Economy Score", 'Economy Score', self.value) 
        if self.economy_score in data:
           # self.value = data[self.economy_score].Value
           # self.inverted = data[self.economy_score].GetProperty('Inverted')
            #self.currency = data[self.economy_score].GetProperty('USDNOK')
            self.prediction = data[self.economy_score].GetProperty('Prediction')

            
        #if not self.Portfolio.Invested:
        #self.SetHoldings("SPY", -0.5)self.value, self.inverted,
        return self.prediction
    
    def rebalance(self):
    # if this time period the stock are not going to be long/short, liquidate it.
        #economy = self.value
        #inversion = self.inverted
        prediction = self.prediction
        #if data.ContainsKey(self.Symbol):
        #    value = data[self.symbol].Value
       # self.Debug("Economy Score: " + str(economy))
        
        long_list = self.long
        spy = self.spy

        for i in self.Portfolio.Values:
            if (i.Symbol != "SPY"):
                if (i.Invested) and (i.Symbol not in long_list):
                    self.Liquidate(i.Symbol) and self.RemoveSecurity(i.Symbol)
       
        self.Liquidate("SPY")
        for i in self.long:
                self.SetHoldings(i, 1/self.num_fine)  

        
        self.reb = 1

        
        
        invested = [x.Key for x in self.Portfolio if x.Value.Invested]
        
        for symbol in invested:
            security_holding = self.Portfolio[symbol]
            #total_holding = security_holding.TotalHoldingsValue
            quantity = security_holding.Quantity
            price = security_holding.AveragePrice
            self.Debug(str(symbol) + " " + str(quantity))


class EconomyScore(PythonData):

    #sia = SentimentIntensityAnalyzer()

    def GetSource(self, config, date, isLive): #Gets source of data.
        source = "https://www.dropbox.com/s/v8js30v5yftjog6/finalscores1986.csv?dl=1"
        #source = "https://www.dropbox.com/s/run9sly7c3rfq02/finalscores.csv?dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile); # 

    def Reader(self, config, line, date, isLive): # Read the custom data. We need to specify structure of the data. 
        if not (line.strip() and line[0].isdigit()): #To make sure we dont use the data from the header index, and dont continue if theres no data left.
            return None
        
        data = line.split(',') # OTherwie we split at the commas, as per CSV files. 
        score = EconomyScore() # Now we save the data to the data variable. 
        
        try:
            score.Symbol = config.Symbol #For the symbol always use conifg.Symbol
            score.Time = datetime.strptime(data[0], '%Y-%m-%d') + timedelta(hours=0) #Could also use timedelta(hours=20) We add some time here because we dont want the data to be accessed before its known. (Look ahead bias)
            content = data[1].lower() 
            
           # score.Value = float(data[1])
           # score['Inverted'] = float(data[2])
            score['Prediction'] = float(data[1])
            #score['USDNOK'] = float(data[5])
            #score.Inverted = float(data[2])
            return score



            #if "tsla" in content or "tesla" in content:
            #    tweet.Value = self.sia.polarity_scores(content)["compound"]
            #else:
            #    score.Value = 0
            
            #tweet["Tweet"] = str(content)
            
        except ValueError:
            return None
        
        return score
