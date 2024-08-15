# web_scraping
The goal of the project was to do an analysis of 2024 Elections results using two websites https://results.eci.gov.in/. and https://www.myneta.info/. The ECI website contains information about the vote distribution of each party in each constituency of each state, while the My Neta website contains information about the candidates of each party in each constituency of each state. 

Taken:
1.	Scraping Data
**ECI Website**
I first scraped the data from the ECI website, for which I used the python libraries selenium, pandas and requests. I made a for loop to go through all 9 of the URLs which contained union territories and all 36 URLs which contained the states. Since the web page for union territories and states were the same. I utilized multithreading to make the process easier and run two loops simultaneously.  I saved the data in a data frame combined winners and extracted it to excel.
2. I was given a dataset that had some features matching the data I scraped but it was not exaxtly the same. To combine the two dataframes, I used a python library called Fuzzy Wuzzy to combine them- with an 80% threshold. If the unique id's match by 80% they will be combined.
