dbname=$1
now=$(date +"%m_%d_%Y")
sudo su - postgres
pg_dump -Fc -d"$dbname"  > /webapps/"$dbname"/db/"$dbname"_"$now".dump
psql -d"$dbname" -f import_document_type_attributes.sql
