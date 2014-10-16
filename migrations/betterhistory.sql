ALTER TABLE transactions ADD lastname VARCHAR(127);
ALTER TABLE transactions ADD firstname VARCHAR(127);
ALTER TABLE transactions ADD deletable BOOLEAN DEFAULT TRUE;

-- Associate lastname and firstname with transactions
UPDATE transactions INNER JOIN notes
SET transactions.lastname=notes.lastname,
	transactions.firstname=notes.firstname
WHERE transactions.note = notes.nickname

-- Ecocup will not be deletable
UPDATE transactions SET deletable=FALSE wHERE BINARY(product)=BINARY("Ecocup");
