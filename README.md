# tgminiapp
My default code for creating TelegramMiniApps

https://medium.com/@deltarfd/how-to-set-up-nginx-on-ubuntu-server-fc392c88fb59

server {
   listen 80;
   server_name 94.198.217.245;  # Replace with your domain or IP

   location / {
       proxy_pass http://0.0.0.0:4500;  # Point to Uvicorn
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
}