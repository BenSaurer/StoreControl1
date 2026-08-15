@echo off
set FECHA=%date:~-4%%date:~3,2%%date:~0,2%
pg_dump -U postgres -d storecontrol_db -F c -f backups/storecontrol_%FECHA%.backup
echo Respaldo completado.

