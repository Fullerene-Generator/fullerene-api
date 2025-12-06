# fullerene-api

## włączenie w Dockerze

1. git submodule update --init --recursive
2. docker compose up -d
3. serwer działa na porcie 8000

W przypadku update'u w generatorze, który chcemy odzwierciedlić w serwerze należy przejść te kroki jeszcze raz
z tym, że do polecenia nr 2 dodajemy flagę --build

## włączenie lokalnie

1. Odkomentuj odpowiedni linijki w config.py
2. uzupełnij plik .env
3. uvicorn app.main:app --reload

