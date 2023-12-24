# Time series compression for ZigZag indicator

## The Repository

**Disclaimer:** This repository is personal, and its content does not represent the views or work of the repository owner's past or current employer. It consists of personal projects and is not affiliated with any company or organisation. All code and content within are independent, solely reflecting the owner's personal interests and learning.

## ZigZag compression

### Abstract

The ZigZag indicator is a technical analysis tool used in trading to help identify significant price swings in financial time series data for stocks, forex, or commodities. Its primary function is to filter out minor price fluctuations and highlight larger movements, which are often considered more significant for making informed trading decisions.

Traditionally, ZigZag indicators are calculated from already compressed time series, such as hourly or daily charts. However, this traditional approach may introduce inaccuracies and potentially overlook important price swings within shorter time intervals. In this work, we propose an alternative method for compressing raw time series, ensuring the preservation of all price swings that are greater than or equal to a given threshold of swing size. This approach is based on precomputed numeric importance values assigned to individual data points within the time series.

### Project Files

[\_\_init\_\_.py](__init__.py) Python module directory marker.

[zzcomp.py](zzcomp.py) Implementation of ZigZag time series compression, which includes functions for compression, recompression and calculating ZigZag indicator from the compressed time series.

[demo_zzcomp.py](demo_zzcomp.py) Demonstration of ZigZag compression with four samples, including a random walk. Download this file and the two files above into the same directory, then execute this Python script. Executing this script will open ten windows, each displaying the ZigZag indicator with different parameters. To selectively turn them off, update the SAMPLES_TO_PLOT list variable in the source file.

[Time_series_compression_for_ZigZag_indicator.md](Time_series_compression_for_ZigZag_indicator.md) A draft paper that provides the technical background of ZigZag compression.

## License

Copyright (c) Egidijus Andriuskevicius. All rights reserved.

Licensed under the [MIT](LICENSE) license.
