1. put a file with name "dump.dump" to "input" directory
2. run command from "anonymizer" directory:
    docker build -t anonymizer .
3. run command:
    docker run --rm -v ./outcome:/outcome --name anonymizer -e POSTGRES_USER=anonymizer -e POSTGRES_PASSWORD=anonymizer -e POSTGRES_DB=anonymizer anonymizer
4. after finished previous command (it takes some time - as much as big is dump.dump file) get file "anonymized_dump.tar" in "outcome" directory