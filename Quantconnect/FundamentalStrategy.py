#This is a Template of dynamic stock selection.
#You can try your own fundamental factor and ranking method by editing the CoarseSelectionFunction and FineSelectionFunction
import operator
from math import ceil,floor
from itertools import groupby
from datetime import datetime, timedelta

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

    def Initialize(self):
        self.SetCash(13000)
        self.SetStartDate(2022,3,1)
        self.SetEndDate(2022,3,20) # if not specified, the Backtesting EndDate would be today 
        
    
        self.spy = self.AddEquity("QQQ", Resolution.Daily).Symbol
        self.SetBenchmark('QQQ')
        
        self.UniverseSettings.Resolution = Resolution.Daily
        
        self.AddUniverse(self.CoarseSelectionFunction,self.FineSelectionFunction)
        
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
        self.SetAlpha(ConstantAlphaModel(InsightType.Price, InsightDirection.Up, timedelta(30)))

    # Schedule the rebalance function to execute at the begining of each week
        self.Schedule.On(self.DateRules.EveryDay(self.spy), 
        self.TimeRules.AfterMarketOpen(self.spy,180), Action(self.rebalance))
        
    
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
    
        filtered_fine = [x for x in fine if x.OperationRatios.OperationMargin.ThreeMonths
                                            #and x.OperationRatios.OperationMargin.OneYear
                                            #and x.OperationRatios.RevenueGrowth.OneYear
                                            and x.OperationRatios.RevenueGrowth.ThreeMonths
                                            #and x.OperationRatios.RevenueGrowth.ThreeYears
                                            #and x.OperationRatios.AssetsTurnover.OneYear
                                            and x.OperationRatios.AssetsTurnover.ThreeMonths
                                            and x.OperationRatios.EBITDAMargin.ThreeMonths
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
                                            #and x.OperationRatios.ROE.ThreeMonths
                                            #and x.OperationRatios.ROIC.ThreeMonths
                                            #and x.OperationRatios.ROA.ThreeMonths
                                            #and x.OperationRatios.FinancialLeverage.OneYear
                                            #and x.FinancialStatements.IncomeStatement.ResearchAndDevelopment.ThreeMonths=> 0
                                            #and x.ValuationRatios.TrailingDividendYield < 0.005
                                            #and x.OperationRatios.NetIncomeGrowth.Value!=0
                                            and x.OperationRatios.StockholdersEquityGrowth.OneYear
                                            and x.SecurityReference.IsPrimaryShare > 0
                                            #and (x.AssetClassification.FinancialHealthGrade!="F")
                                            #and (x.AssetClassification.FinancialHealthGrade!="E")
                                            #and x.FinancialStatements.IncomeStatement.TotalRevenue.TwelveMonths
                                            #and x.SecurityReference.SecurityType == "ST00000001"
                                            and (x.AssetClassification.MorningstarSectorCode!= 309)
                                            and (x.AssetClassification.MorningstarSectorCode!=206)
                                            and (x.AssetClassification.MorningstarIndustryGroupCode!=31055)]
                                            
        #for i in filtered_fine:
        
             #i.rd_ratio = (i.FinancialStatements.IncomeStatement.ResearchAndDevelopment.ThreeMonths / i.FinancialStatements.IncomeStatement.NetIncome.ThreeMonths)
        
             #i.MarketCapi = (i.EarningReports.BasicAverageShares.TwelveMonths *
               #             i.EarningReports.BasicEPS.TwelveMonths *
            #                i.ValuationRatios.PERatio)
             #rd_ratio[i] = (i.FinancialStatements.IncomeStatement.ResearchAndDevelopment.ThreeMonths / 
             #               i.FinancialStatements.IncomeStatement.NetIncome.OneYear)
            
            #market_cap[i] = (i.EarningReports.BasicAverageShares.ThreeMonths *
            #               i.EarningReports.BasicEPS.TwelveMonths *
            #               i.ValuationRatios.PERatio)
           
                                    
    
                                        
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
        
        sortedByfactor14 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.PERatio, reverse=False)
        
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
        
        #sortedByfactor36 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.TotalYield, reverse=True)
        
        #sortedByfactor37 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.SecondYearEstimatedEPSGrowth, reverse=False)
        
        #ValuationRatios.SecondYearEstimatedEPSGrowth
        
        #OperationRatios.GrossMargin5YrAvg.FiveYears
        
        #sortedByfactor32 = sorted(filtered_fine, key=lambda x: x.OperationRatios.GrossMargin.OneYear, reverse=True)
        
    
        #sortedByfactor34 = sorted(filtered_fine, key=lambda x: x.OperationRatios.CapExSalesRatio.OneYear, reverse=False)
       
        
       
        
        #sortedByfactor22 = sorted(filtered_fine, key=lambda x: x.OperationRatios.CapExSalesRatio.OneYear, reverse=False)
        
        #sortedByfactor21 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.TrailingDividendYield, reverse=True)
        
        #sortedByfactor15 = sorted(filtered_fine, key=lambda x: x.ValuationRatios.TrailingDividendYield, reverse=True)
        #sortedByfactor10 = sorted(filtered_fine, key=lambda x: x.OperationRatios.OperationMargin.ThreeMonths, reverse=False)
        
        #sortedByPEvol = sorted(filtered_fine, key=lambda x: x.pevol) 
        
        #sortedByrd_ratio = sorted(filtered_fine, key=lambda x: x.rd_ratio)  
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
                #esteps = sortedByfactor37.index(ele)
                #pe_growth = sortedByfactor36.index(ele)
                #gross_margin1 = sortedByfactor32.index(ele)
                #capexsales = sortedByfactor34.index(ele)
                
                #capex_turnover = sortedByfactor22.index(ele)
                #div_yield = sortedByfactor36.index(ele)
                #leverage = sortedByfactor16.index(ele)
                #dividend_yield = sortedByfactor15.index(ele)
                #rd_ratio = sortedByrd_ratio.index(ele)
                #equity_growth = sortedByfactor10.index(ele)
                #margin1 = sortedByfactor10.index(ele)
                
                score = [] #Assign weights to each factor here, example: [(revenue_growth)*40, (margin)*2, ....]
                         
                         
                score = sum(score)
                stock_dict[ele] = score
               
                
        
        # sort the stocks by their scores
        self.sorted_stock = sorted(stock_dict.items(), key=lambda d:d[1],reverse=True)
        sorted_symbol = [x[0] for x in self.sorted_stock]
          

        # sort the top stocks into the long_list and the bottom ones into the short_list
        self.long = [x.Symbol for x in sorted_symbol[:self.num_fine]] # Adjust in sorted_symbol[] if you want to remove outliers or specify how many stocks in self long will be added
        
        return self.long
        
                    
    def OnData(self, data):
        
        #if not self.Portfolio.Invested:
        #self.SetHoldings("SPY", -0.5)
        pass
    
    def rebalance(self):
    # if this month the stock are not going to be long/short, liquidate it.
        long_list = self.long
        spy = self.spy
        #self.SetHoldings("QQQ", -0.2) 
        for i in self.Portfolio.Values:
            #if (i.Symbol != "QQQ"):
            if (i.Invested) and (i.Symbol not in long_list):
                self.Liquidate(i.Symbol) and self.RemoveSecurity(i.Symbol)
                
        #self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
              #(i.Symbol != "SPY")
                    
    # Alternatively, you can liquidate all the stocks at the end of each month.
    # Which method to choose depends on your investment philosiphy 
    # if you prefer to realized the gain/loss each month, you can choose this method.
    
        #self.Liquidate()
        
    # Assign each stock equally. Alternatively you can design your own portfolio construction method
        #self.SetHoldings(self.long[0], 2/self.num_fine)
       # for i in self.long[:1]:
            # self.SetHoldings(i, 2/self.num_fine)
            #    else:
      #      self.SetHoldings(i, 1.6/(self.num_fine))
            
       # for i in self.long[2:4]:
    #        # self.SetHoldings(i, 2/self.num_fine)
            #    else:
     #       self.SetHoldings(i, 0.96/(self.num_fine))
            
        for i in self.long:
            # self.SetHoldings(i, 2/self.num_fine)
            #    else:
            #self.SetHoldings(i, self.Portfolio.TotalPortfolioValue*(1/self.num_fine)/self.Portfolio.TotalPortfolioValue)
            self.SetHoldings(i, 1/self.num_fine)
            #self.SetHoldings(i, (0.5)/(self.num_fine))
            
        
        
        self.reb = 1
       # for i in self.short:
    #        self.SetHoldings(i, -0.9/self.num_fine) # For shorting

        
            
        invested = [x.Key for x in self.Portfolio if x.Value.Invested]
        
        for symbol in invested:
            security_holding = self.Portfolio[symbol]
            #total_holding = security_holding.TotalHoldingsValue
            quantity = security_holding.Quantity
            price = security_holding.AveragePrice
            self.Debug(str(symbol) + " " + str(quantity))
