import pandas as pd
from pystock.method.method import Method
# import matplotlib.pyplot as plt
from pystock.attributes.attribute import Field


class MACD(Method):

    short_term = Field()
    long_term = Field()
    macd_span = Field()

    def __init__(
            self,
            stock_df: pd.DataFrame = None,
            short_term: int = 12,
            long_term: int = 26,
            macd_span: int = 9):
        super().__init__()
        self.short_term = short_term
        self.long_term = long_term
        self.macd_span = macd_span

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        """
        macdを基準として今後上昇するかどうかをスコアで返す。
        値が大きければその傾向が高いことを表している。
        最小値は0で、最大値は無限大である。
        :param _df:
        :return:
        """
        # histogramが図として表現されるMACDの値
        _df = _df.assign(
            # MACDの計算
            ema_short=lambda x: x['close'].ewm(span=self.short_term).mean(),
            ema_long=lambda x: x['close'].ewm(span=self.long_term).mean(),
            macd=lambda x: x['ema_short'] - x['ema_long'],
            signal=lambda x: x['macd'].ewm(span=self.macd_span).mean(),
            # ヒストグラム値
            histogram=lambda x: x['macd'] - x['signal'],
        )
        return _df

    def signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        # 正負が交差した点
        _df = _df.join(self.cross(_df['histogram']))
        _df = _df.rename(columns={
            "to_plus": "buy_signal",
            "to_minus": "sell_signal"
        })
        return _df

    # def visualize(self, _df: pd.DataFrame):
    #     fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(6, 5))
    #     # x軸のオートフォーマット
    #     fig.autofmt_xdate()
    #
    #     # set candlestick
    #     self.add_ax_candlestick(ax1, _df)
    #
    #     # plot macd
    #     ax2.plot(_df.index, _df['macd'], label="macd")
    #     ax2.plot(_df.index, _df['signal'], label="signal")
    #     ax2.bar(_df.index, _df['histogram'], label="histogram")
    #     ax2.legend(loc="center left")  # 各線のラベルを表示
    #
    #     ax1.legend(loc="best")  # 各線のラベルを表示
    #     return fig