# Capriole Task

## Overview

Scrapping data from data source provided by capriol and storing the data in SQL database.

## Data Source

1) https://data.bitcoinity.org/markets/volume/30d?c=e&t=b
2) https://data.bitcoinity.org/markets/books/USD
3) https://data.bitcoinity.org/markets/rank/30d/USD?c=e&r=hour&t=ae
4) https://bitinfocharts.com/top-100-richest-bitcoin-addresses.html
5) https://www.coinoptionstrack.com/options/BTC/open-interest

## Required Python Packages

- requests
- json
- datetime
- sqlite3
- random
- lxml

## Crawler Logic

- python request library used to scrap the data from the given data sources.
- Free proxies are used to overcome blocking issue (source: https://www.proxynova.com/).
- Data extraction is done by using the package lxml and json.
- Stored all extracted data in to sql database

## Operations used in sqllite

- CREAT: Created the table if the table not exists.
- INSERT: Inserting the data if the data is nt present in the table.
- UPDATE: Updated the table if data already exists.

## Cron setup

- Daily Cron: (0 1 * * *) This cron will run every dat at 1:00 AM
- Hourly Cron: (0 */1 * * *) This cron will run At minute 0 past every hour

For setting up cron we need to have AWS EC2 server

##  Setting Up AWS Server

- Go to AWS console
- Check for EC2
- Make a configuration as you required
- Download the .pem file and create EC2 server (filename.pem)
- Then check the IP for that EC2 server 
- and execute this EX: ssh –i path_to_pem_file ubuntu@ec2-XX-XX-XXX-XXX.uswest-2.compute.amazonaws.com

## Executing the Crawler

We can run the crawler by simply executing file filename.py
