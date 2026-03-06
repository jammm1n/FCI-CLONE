C — Context:
You are analyzing a dataset containing records of failed fiat transactions with various error reasons and timestamps.

R — Role:
You are a data analyst tasked with summarizing key insights from the data.

A — Action:
Summarize the most used error reasons, the date range of the failed fiat transactions, and identify any fiat channels that have error reasons related to "suspected fraud." Then provide the total value of the failed fiat transactions. All local currency amounts must include USD equivalent in square brackets.

F — Format:
Provide a concise summary in one simple paragraph, no more than 3 sentences, using the date format YYYY-MM-DD. Follow this template as a guide:
"The most used error reason for the failed fiat transactions are XXX. (only include if there are reasons for 'suspected fraud') The fiat channels that rejected the deposits for suspected fraud were (fiat channel). The User conducted a total of (count) failed fiat transactions for suspected fraud between YYYY-MM-DD and YYYY-MM-DD with a value totaling XXX. These failed deposits occurred between (date range)."

T — Target Audience:
The summary is intended for Binance operations and compliance teams who need a clear and professional overview of failed fiat transaction issues.
