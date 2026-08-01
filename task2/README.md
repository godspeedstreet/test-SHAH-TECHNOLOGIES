# Как проверял

### Cкриншоты:

<img width="3107" height="1741" alt="prsc2" src="https://github.com/user-attachments/assets/56e14d6f-d963-4e58-af28-f211fe99c509" />
<img width="3101" height="1045" alt="prsc1" src="https://github.com/user-attachments/assets/1aa1fc15-78de-47a3-9285-faddb70fb63a" />
<img width="3105" height="1749" alt="prsc3" src="https://github.com/user-attachments/assets/ebdda651-94ed-4c72-82c3-265192c7fd3c" />


### Как проверял: 

При первом запуске возникла ошибка и страница не запускалась. Numeric из Postgres сериализировалась в JSON как строка "4.5", а не число. Number() решает это. После доработки страница открылась без ошибок. Из багов: не работали кнопки «Назад»/«Вперед» для перехода между страницами таблицы из-за того, что при смене страницы срабатывал эффект, который сбрасывал страницу на 1. 


