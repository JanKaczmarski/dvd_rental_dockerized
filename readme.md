1. docker-compose up --build
2. Connect to the postgres container from terminal
- open terminal
- docker ps
- docker exec -it <postgres-container-id> bash
3. Paste this into terminal and run
- pg_restore -U postgres --dbname=dvd_rental --verbose /home/dvd_backup.tar
4. Check if data is restored
- psql -U postgres
- \c dvd_rental
- \d 
5. If 35 tables(rows) appear it's all good