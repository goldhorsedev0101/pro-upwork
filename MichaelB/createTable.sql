CREATE TABLE IF NOT EXISTS coinPrices (
    id INTEGER PRIMARY KEY, 
	name TEXT NULL,
	symbol TEXT NULL,
	datePrice DATE NULL,
	open REAL NULL,
	high REAL NULL,
	low REAL NULL,
	close REAL NULL,
	volume REAL NULL,
	market_cap REAL NULL,
	timestamp TEXT NULL
);