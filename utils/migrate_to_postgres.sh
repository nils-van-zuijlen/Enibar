export_table() {
    table=$1
    echo "exporting ${table}..."
    mysql -uroot enibar -e "SELECT * FROM $table" | sed 's/\t/|/g' > enibar.$table.psv
    #Remove header
    remove_first_line "enibar.$table.psv"
}

remove_first_line() {
    file=$1
    echo "$(tail -n +2 $file)" > $file
}

import_table() {
    table=$1

    echo "importing $table.."
    psql -d enibar -c "\copy $table from 'enibar.${table}.psv' DELIMITERS '|' NULL 'NULL' CSV;"
}

for table in  "admins" "categories" "mail_models" "note_categories" "note_categories_assoc" "notes" "panel_content" "panels" "price_description" "prices" "products" "scheduled_mails" "transactions"
do
    export_table $table
done

remove_first_line enibar.admins.psv
psql -d enibar -c "DELETE FROM note_categories"

for table in  "admins" "categories" "mail_models" "note_categories" "notes" "note_categories_assoc" "panels" "products" "panel_content" "price_description" "prices" "scheduled_mails" "transactions"
do
    import_table $table
done

for table in  "categories" "note_categories" "notes" "note_categories_assoc" "panels" "products" "price_description" "prices" "transactions"
do
    id=$(psql -d enibar -c "SELECT id FROM $table ORDER BY id DESC LIMIT 1" | sed "1d" | sed "1d" | sed "2d")
    psql -d enibar -c "SELECT setval('${table}_id_seq', $id)"
done
