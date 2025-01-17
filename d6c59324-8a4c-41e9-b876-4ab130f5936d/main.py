from surmount.base_class import Strategy, TargetAllocation
from surmount.data import InsiderTrading, Dividend, FinancialStatement, InstitutionalOwnership
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Selecting a mix of tickers known for consistent growth and dividends
        self.tickers = ["AAPL", "MSFT", "JNJ", "XOM"]
        self.data_list = [Dividend(i) for i in self.tickers] + \
                         [FinancialStatement(i) for i in self.tickers] + \
                         [InstitutionalOwnership(i) for i in self.tickers]
                         
    @property
    def interval(self):
        # Using daily data to make decisions
        return "1day"

    @property
    def assets(self):
        # Assets under consideration
        return self.tickers

    @property
    def data(self):
        # Data required for the decision-making process
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        # Filtering based on criteria: Steady profit & dividend growth, solid institutional ownership
        for ticker in self.tickers:
            # Ensuring data availability before proceeding
            if not (data[("financial_statement", ticker)] and data[("dividend", ticker)] and data[("institutional_ownership", ticker)]):
                continue
            
            fs_data = data[("financial_statement", ticker)][-1]  # Using the latest financial statement
            div_data = data[("dividend", ticker)][-1]  # Latest dividend record
            inst_ownership = data[("institutional_ownership", ticker)][-1]  # Latest institutional ownership data

            # Basic checks for growth, positive dividends, and significant institutional support
            if fs_data['revenue'] > fs_data['costOfRevenue'] and \
               div_data['dividend'] > 0 and \
               inst_ownership['ownershipPercent'] > 50:
                # This is a simplistic filter; real strategies would need more sophisticated analytics
                allocation_dict[ticker] = 0.25  # Equal allocation if passing the filter
            else:
                allocation_dict[ticker] = 0  # Excluding stocks not meeting criteria

        # Normalizing allocations to ensure the sum doesn't exceed 1
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 0:
            for ticker in allocation_dict:
                allocation_dict[ticker] /= total_allocation

        return TargetAllocation(allocation_dict)