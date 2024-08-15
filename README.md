# web_scraping
The goal of the project was to do an analysis of 2024 Elections results using two websites https://results.eci.gov.in/. and https://www.myneta.info/. The ECI website contains information about the vote distribution of each party in each constituency of each state, while the My Neta website contains information about the candidates of each party in each constituency of each state. 

Taken:
1.	**Scraping Data**

I first scraped the data from the ECI website, for which I used the python libraries selenium, pandas and requests. I made a for loop to go through all 9 of the URLs which contained union territories and all 36 URLs which contained the states. Since the web page for union territories and states were the same. I utilized multithreading to make the process easier and run two loops simultaneously.  I saved the data in a data frame combined winners and extracted it to excel.
2. **Combining Datasets**
I was given a dataset that had some features matching the data I scraped but it was not exaxtly the same. To combine the two dataframes, I used a python library called Fuzzy Wuzzy to combine them- with an 80% threshold. If the unique id's match by 80% they will be combined.

3. **Made a streamlit app**
I built an app using the Streamlit library in Python to showcase all the visualizations created from combined dataframes. The app includes treemaps, pie charts, and bar charts, and utilizes a JSON map of India to display which political party won in different regions of the country, down to the level of individual constituencies.

4. **Django app**
Using the Streamlit app as a reference, I developed a Django application for the company I worked for. I also enhanced the mapping functionality by integrating D3.js and Plotly.js, allowing users to drill down into the map and apply filters. This enables users to explore specific regions, states, or constituencies within India and view areas with higher concentrations of Muslim populations based on the selected filters.