FROM nginx:alpine

# Mini App: страница-движок + данные предметов (манифест и JSON-файлы курсов).
COPY index.html /usr/share/nginx/html/index.html
COPY data/ /usr/share/nginx/html/data/

# nginx:alpine по умолчанию слушает 80 и отдаёт /usr/share/nginx/html
EXPOSE 80
