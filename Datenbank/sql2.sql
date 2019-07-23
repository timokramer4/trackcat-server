SELECT 
    users.id,
    firstName,
    lastName,
    image,
    dateOfRegistration,
    email,
    CASE
        WHEN liveRecords.users_id > 0 THEN 1
        ELSE 0
    END AS isLive
FROM
    users
        LEFT JOIN
    users_has_users ON users.id = users_has_users.asker
        OR users.id = users_has_users.asked
        LEFT JOIN
    liveRecords ON liveRecords.users_id = users.id
WHERE
    users.id != 1 AND areFriends = 1
        AND (users_has_users.asker = 1
        OR users_has_users.asked = 1)
        AND (UPPER(firstName) LIKE UPPER('%')
        OR UPPER(lastName) LIKE UPPER('%')
        OR UPPER(email) LIKE UPPER('%'))
        AND UPPER(email) != UPPER('test@trackcat.de')
LIMIT 0 , 10